// MemoryLens Frontend App — Phase 4 Clarifying Question Flow & Enhanced Search

let state = {
  photos: [],
  searchMode: 'ai', // 'ai' or 'literal'
  currentQuery: '',
  activeRefinement: null,
  isSkipped: false,
  selectedPhoto: null
};

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  await loadPhotos();
  setupEventListeners();
  renderHomeLibrary();
});

// LocalStorage helpers for browser-isolated privacy
const STORAGE_KEY = 'memorylens_user_photos';

function getLocalPhotos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Error reading localStorage:', e);
    return [];
  }
}

function saveLocalPhoto(photo) {
  const list = getLocalPhotos();
  list.unshift(photo);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

function clearLocalPhotos() {
  localStorage.removeItem(STORAGE_KEY);
}

// Update UI banner to reflect private testing state
function updateBannerForLocalPhotos(localCount) {
  const banner = document.getElementById('phaseBanner');
  const bannerText = document.getElementById('bannerText');
  if (!banner || !bannerText) return;

  if (localCount > 0) {
    bannerText.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; flex-wrap: wrap; gap: 10px;">
        <span><strong>🔒 Private Testing Mode Active:</strong> You have <strong>${localCount}</strong> custom photo(s) stored privately in this browser only. Other users will NOT see them.</span>
        <button id="clearLocalPhotosBtn" style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; font-weight: 600;">Clear My Photos</button>
      </div>
    `;
    const clearBtn = document.getElementById('clearLocalPhotosBtn');
    if (clearBtn) {
      clearBtn.onclick = async () => {
        if (confirm('Clear your private photos from this browser?')) {
          clearLocalPhotos();
          showToast('Cleared your private photos.');
          await loadPhotos();
          renderHomeLibrary();
        }
      };
    }
  } else {
    bannerText.innerHTML = `
      <strong>Test Retrieval With Your Own Photos:</strong> Click <em>"+ Add Photo"</em> to upload photos with memory tags. Photos stay <strong>100% private to your browser</strong> and are never saved on the server!
    `;
  }
}

// Fetch library dataset from API and merge with private local photos
async function loadPhotos() {
  try {
    const res = await fetch('/api/photos');
    if (!res.ok) throw new Error('Failed to load dataset');
    const seeded = await res.json();
    const local = getLocalPhotos();
    state.photos = [...local, ...seeded];
    updateBannerForLocalPhotos(local.length);
    console.log(`MemoryLens: Loaded ${state.photos.length} photos (${local.length} private local, ${seeded.length} seeded).`);
  } catch (err) {
    console.error('Error loading dataset:', err);
  }
}

// Setup Event Listeners
function setupEventListeners() {
  const searchInput = document.getElementById('searchInput');
  const clearBtn = document.getElementById('clearSearchBtn');
  const resetBtn = document.getElementById('resetSearchBtn');
  const brandHomeBtn = document.getElementById('brandHomeBtn');
  const toggleGroup = document.getElementById('modeToggle');

  // Real-time & Enter Key Search Listener
  let debounceTimer;
  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.trim();
    clearBtn.style.display = q ? 'block' : 'none';
    
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      if (q) {
        performSearch(q);
      } else {
        renderHomeLibrary();
      }
    }, 300);
  });

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      clearTimeout(debounceTimer);
      const q = searchInput.value.trim();
      if (q) performSearch(q);
    }
  });

  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    renderHomeLibrary();
  });

  resetBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    renderHomeLibrary();
  });

  brandHomeBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    renderHomeLibrary();
  });

  // Mode Toggle Listener
  toggleGroup.addEventListener('click', (e) => {
    if (e.target.classList.contains('toggle-btn')) {
      document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.searchMode = e.target.dataset.mode;
      console.log(`Search Mode switched to: ${state.searchMode}`);
      
      if (state.currentQuery) {
        performSearch(state.currentQuery, state.activeRefinement, state.isSkipped);
      }
    }
  });

  // Lightbox Close Handlers
  document.getElementById('lightboxClose').addEventListener('click', closeLightbox);
  document.getElementById('lightbox').addEventListener('click', (e) => {
    if (e.target.id === 'lightbox') closeLightbox();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (state.selectedPhoto) closeLightbox();
      const addModal = document.getElementById('addPhotoModal');
      if (addModal && addModal.classList.contains('open')) {
        addModal.classList.remove('open');
      }
    }
  });

  // =========================================================================
  // Add Photo Modal & Form Handlers
  // =========================================================================
  const openAddPhotoBtn = document.getElementById('openAddPhotoBtn');
  const closeAddPhotoBtn = document.getElementById('closeAddPhotoBtn');
  const cancelAddPhotoBtn = document.getElementById('cancelAddPhotoBtn');
  const addPhotoModal = document.getElementById('addPhotoModal');
  const addPhotoForm = document.getElementById('addPhotoForm');
  const photoFileInput = document.getElementById('photoFileInput');
  const uploadDropzone = document.getElementById('uploadDropzone');
  const dropzoneEmpty = document.getElementById('dropzoneEmpty');
  const dropzonePreview = document.getElementById('dropzonePreview');
  const previewImage = document.getElementById('previewImage');
  const removeImageBtn = document.getElementById('removeImageBtn');
  const imageUrlInput = document.getElementById('imageUrlInput');
  const docToggleHeader = document.getElementById('docToggleHeader');
  const docFieldsContainer = document.getElementById('docFieldsContainer');
  const docToggleArrow = document.getElementById('docToggleArrow');
  const relSuggestions = document.getElementById('relSuggestions');

  let currentImageDataUrl = '';

  if (openAddPhotoBtn) {
    openAddPhotoBtn.addEventListener('click', () => {
      addPhotoModal.classList.add('open');
      addPhotoModal.setAttribute('aria-hidden', 'false');
    });
  }

  function closeAddPhotoModal() {
    if (!addPhotoModal) return;
    addPhotoModal.classList.remove('open');
    addPhotoModal.setAttribute('aria-hidden', 'true');
    addPhotoForm.reset();
    clearSelectedImage();
  }

  if (closeAddPhotoBtn) closeAddPhotoBtn.addEventListener('click', closeAddPhotoModal);
  if (cancelAddPhotoBtn) cancelAddPhotoBtn.addEventListener('click', closeAddPhotoModal);
  if (addPhotoModal) {
    addPhotoModal.addEventListener('click', (e) => {
      if (e.target === addPhotoModal) closeAddPhotoModal();
    });
  }

  // Dropzone File Selection
  if (uploadDropzone && photoFileInput) {
    uploadDropzone.addEventListener('click', (e) => {
      if (e.target !== removeImageBtn && !removeImageBtn.contains(e.target)) {
        photoFileInput.click();
      }
    });

    photoFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0]);
      }
    });

    uploadDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadDropzone.classList.add('dragover');
    });

    uploadDropzone.addEventListener('dragleave', () => {
      uploadDropzone.classList.remove('dragover');
    });

    uploadDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadDropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0]);
      }
    });
  }

  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      showToast('⚠️ Please select an image file (JPG, PNG, WEBP)');
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      currentImageDataUrl = event.target.result;
      previewImage.src = currentImageDataUrl;
      dropzoneEmpty.style.display = 'none';
      dropzonePreview.style.display = 'flex';
    };
    reader.readAsDataURL(file);
  }

  function clearSelectedImage() {
    currentImageDataUrl = '';
    if (previewImage) previewImage.src = '';
    if (photoFileInput) photoFileInput.value = '';
    if (dropzoneEmpty) dropzoneEmpty.style.display = 'flex';
    if (dropzonePreview) dropzonePreview.style.display = 'none';
  }

  if (removeImageBtn) {
    removeImageBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearSelectedImage();
    });
  }

  if (imageUrlInput) {
    imageUrlInput.addEventListener('input', (e) => {
      const url = e.target.value.trim();
      if (url) {
        currentImageDataUrl = url;
        previewImage.src = url;
        dropzoneEmpty.style.display = 'none';
        dropzonePreview.style.display = 'flex';
      }
    });
  }

  // Relationship suggestion chips
  if (relSuggestions) {
    relSuggestions.addEventListener('click', (e) => {
      if (e.target.classList.contains('chip-btn')) {
        const val = e.target.dataset.val;
        const relInput = document.getElementById('relationshipInput');
        const currentVals = relInput.value.split(',').map(s => s.trim()).filter(Boolean);
        if (!currentVals.includes(val)) {
          currentVals.push(val);
          relInput.value = currentVals.join(', ');
        }
      }
    });
  }

  // Document accordion toggle
  if (docToggleHeader && docFieldsContainer && docToggleArrow) {
    docToggleHeader.addEventListener('click', () => {
      const isOpen = docFieldsContainer.style.display !== 'none';
      docFieldsContainer.style.display = isOpen ? 'none' : 'block';
      docToggleArrow.textContent = isOpen ? '▼' : '▲';
    });
  }

  // Add Photo Form Submit
  if (addPhotoForm) {
    addPhotoForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const saveBtn = document.getElementById('savePhotoBtn');
      saveBtn.disabled = true;
      saveBtn.textContent = 'Indexing Photo...';

      try {
        const placeName = document.getElementById('placeNameInput').value.trim();
        const relationships = document.getElementById('relationshipInput').value
          .split(',')
          .map(s => s.trim())
          .filter(Boolean);
        const taggedNames = document.getElementById('taggedNamesInput').value
          .split(',')
          .map(s => s.trim())
          .filter(Boolean);
        const visualDescriptors = document.getElementById('visualDescriptorsInput').value
          .split(',')
          .map(s => s.trim())
          .filter(Boolean);
        const eventTags = document.getElementById('eventTagsInput').value
          .split(',')
          .map(s => s.trim())
          .filter(Boolean);
        const approxDate = document.getElementById('dateRangeInput').value.trim() || 'Recent';
        const docPurpose = document.getElementById('docPurposeInput').value.trim() || null;
        const ocrText = document.getElementById('ocrTextInput').value.trim() || null;

        // Fallback placeholder SVG if no image uploaded
        let finalImageUrl = currentImageDataUrl || (imageUrlInput ? imageUrlInput.value.trim() : '');
        if (!finalImageUrl) {
          const title = placeName || (relationships[0] ? `With ${relationships[0]}` : 'My Photo');
          const subtitle = visualDescriptors.slice(0, 2).join(' & ') || 'Added by user';
          finalImageUrl = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'><rect width='100%' height='100%' fill='%231e293b'/><circle cx='200' cy='120' r='50' fill='%2338bdf8' opacity='0.3'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%23f8fafc' font-family='sans-serif' font-size='16'>${escapeHtml(title)}</text><text x='50%' y='65%' dominant-baseline='middle' text-anchor='middle' fill='%2394a3b8' font-family='sans-serif' font-size='12'>${escapeHtml(subtitle)}</text></svg>`;
        }

        const photo_id = `user_${Date.now()}`;
        const photo_obj = {
          photo_id: photo_id,
          image_url: finalImageUrl,
          place_name: placeName || null,
          relationships: relationships,
          tagged_names: taggedNames,
          visual_descriptors: visualDescriptors,
          event_tags: eventTags,
          approx_date_range: approxDate,
          date_taken: new Date().toISOString(),
          document_purpose: docPurpose,
          ocr_text: ocrText
        };

        // Save privately into this browser's localStorage
        saveLocalPhoto(photo_obj);

        showToast('🔒 Photo saved privately to your browser! No other users can see it.');
        closeAddPhotoModal();
        await loadPhotos();
        renderHomeLibrary();
      } catch (err) {
        console.error('Error adding photo:', err);
        showToast('❌ Failed to save photo: ' + err.message);
      } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save & Index Photo ✨';
      }
    });
  }

  // Toast Helper
  function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 4500);
  }
}

// Helper to format clean photo titles
function getPhotoTitle(photo) {
  if (photo.document_purpose) {
    return photo.document_purpose.charAt(0).toUpperCase() + photo.document_purpose.slice(1);
  }
  if (photo.place_name && !["Home Office", "Family Home"].includes(photo.place_name)) {
    return photo.place_name;
  }
  if (photo.visual_descriptors && photo.visual_descriptors.length > 0) {
    const mainDesc = photo.visual_descriptors[0];
    return mainDesc.charAt(0).toUpperCase() + mainDesc.slice(1);
  }
  if (photo.place_name) return photo.place_name;
  if (photo.event_tags && photo.event_tags.length > 0) {
    return photo.event_tags[0].charAt(0).toUpperCase() + photo.event_tags[0].slice(1);
  }
  return photo.photo_id;
}

// Render Default Home Library Grid
function renderHomeLibrary() {
  state.currentQuery = '';
  state.activeRefinement = null;
  state.isSkipped = false;
  
  document.getElementById('searchHeader').style.display = 'none';
  document.getElementById('phaseBanner').style.display = 'flex';
  
  const container = document.getElementById('viewContainer');
  container.innerHTML = '';

  const groups = groupPhotosByDate(state.photos);
  
  for (const [dateLabel, groupPhotos] of Object.entries(groups)) {
    const groupEl = document.createElement('div');
    groupEl.className = 'date-group';

    const headerEl = document.createElement('div');
    headerEl.className = 'date-group-header';
    headerEl.innerHTML = `📅 <span>${dateLabel}</span> <span style="font-size: 0.75rem; color: var(--text-muted);">(${groupPhotos.length} photos)</span>`;
    groupEl.appendChild(headerEl);

    const gridEl = document.createElement('div');
    gridEl.className = 'photo-grid';

    groupPhotos.forEach(p => {
      const card = createStandardPhotoCard(p);
      gridEl.appendChild(card);
    });

    groupEl.appendChild(gridEl);
    container.appendChild(groupEl);
  }
}

// Execute Search API Call with Optional Feature 2 Clarification / Refinement / Skip
async function performSearch(query, refinement = null, skip = false) {
  state.currentQuery = query;
  state.activeRefinement = refinement;
  state.isSkipped = skip;

  document.getElementById('phaseBanner').style.display = 'none';
  const searchHeader = document.getElementById('searchHeader');
  searchHeader.style.display = 'flex';
  
  const modeLabel = state.searchMode === 'ai' ? 'AI Decomposed' : 'Literal Baseline';
  document.getElementById('searchQueryTitle').textContent = `Results for "${query}"`;

  const container = document.getElementById('viewContainer');
  container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">Analyzing memory signals...</div>';

  try {
    let searchData;
    const localPhotos = getLocalPhotos();

    if (localPhotos.length > 0) {
      // Evaluates against user's private local photos in memory for this user only
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          q: query,
          mode: state.searchMode,
          refinement: refinement,
          skip: skip,
          custom_photos: localPhotos
        })
      });
      if (!res.ok) throw new Error('Search API request failed');
      searchData = await res.json();
    } else {
      let url = `/api/search?q=${encodeURIComponent(query)}&mode=${state.searchMode}`;
      if (refinement) url += `&refinement=${encodeURIComponent(refinement)}`;
      if (skip) url += `&skip=true`;

      const res = await fetch(url);
      if (!res.ok) throw new Error('Search API request failed');
      searchData = await res.json();
    }

    document.getElementById('searchMatchCount').textContent = `${searchData.total_matches} photo${searchData.total_matches === 1 ? '' : 's'} matched (${modeLabel})`;

    if (searchData.zero_match || searchData.results.length === 0) {
      renderEmptyState(query);
      return;
    }

    container.innerHTML = '';

    // Render Feature 2 Inline Clarifying Question Card if query is ambiguous & not yet clarified or skipped
    if (searchData.is_ambiguous && searchData.clarifying_question && state.searchMode === 'ai') {
      const questionCard = createClarifyingQuestionCard(searchData.clarifying_question, query);
      container.appendChild(questionCard);
    }

    // STRICT SHORTLIST CAP: Render maximum 8 results per PRD §4.3
    const shortlistResults = searchData.results.slice(0, 8);
    renderShortlistGrid(container, shortlistResults, searchData.total_matches, refinement, skip);

  } catch (err) {
    console.error('Error during search execution:', err);
    container.innerHTML = '<div style="text-align: center; padding: 40px; color: #ef4444;">Error executing search query.</div>';
  }
}

// Create Inline Clarifying Question Card DOM Element (Feature 2)
function createClarifyingQuestionCard(qData, query) {
  const card = document.createElement('div');
  card.className = 'clarifying-card';

  const headerRow = document.createElement('div');
  headerRow.className = 'clarifying-header-row';

  const badge = document.createElement('div');
  badge.className = 'clarifying-badge-tag';
  badge.innerHTML = `💡 Feature 2 Clarification • 1 Question Max`;

  const skipBtn = document.createElement('button');
  skipBtn.className = 'skip-clarifying-btn';
  skipBtn.textContent = 'Skip / Show all results';
  skipBtn.addEventListener('click', () => performSearch(query, null, true));

  headerRow.appendChild(badge);
  headerRow.appendChild(skipBtn);

  const qText = document.createElement('div');
  qText.className = 'clarifying-question-text';
  qText.textContent = qData.question;

  const chipsGroup = document.createElement('div');
  chipsGroup.className = 'option-chips-group';

  qData.options.forEach(opt => {
    const chip = document.createElement('button');
    chip.className = 'option-chip-btn';
    chip.innerHTML = `<span>${opt}</span> →`;
    chip.addEventListener('click', () => performSearch(query, opt));
    chipsGroup.appendChild(chip);
  });

  // Custom text refinement box
  const customRow = document.createElement('div');
  customRow.className = 'clarifying-custom-input-row';
  
  const customInput = document.createElement('input');
  customInput.type = 'text';
  customInput.className = 'clarifying-input';
  customInput.placeholder = 'Or type custom detail (e.g. Paris)...';

  const submitBtn = document.createElement('button');
  submitBtn.className = 'refine-submit-btn';
  submitBtn.textContent = 'Refine';

  const submitAction = () => {
    const val = customInput.value.trim();
    if (val) performSearch(query, val);
  };

  submitBtn.addEventListener('click', submitAction);
  customInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitAction();
  });

  customRow.appendChild(customInput);
  customRow.appendChild(submitBtn);

  card.appendChild(headerRow);
  card.appendChild(qText);
  card.appendChild(chipsGroup);
  card.appendChild(customRow);

  return card;
}

// Render Shortlist Grid with Cap & Refinement Status Banners
function renderShortlistGrid(container, results, totalMatches, refinement, skip) {
  let statusBannerHtml = '';
  
  if (refinement) {
    statusBannerHtml = `<div style="margin-bottom: 16px; font-size: 0.8rem; color: #2dd4bf; background: rgba(45, 212, 191, 0.1); border: 1px solid rgba(45, 212, 191, 0.25); padding: 8px 14px; border-radius: 8px;">✓ <strong>Results Refined:</strong> Narrowed shortlist using follow-up answer "${escapeHtml(refinement)}".</div>`;
  } else if (skip) {
    statusBannerHtml = `<div style="margin-bottom: 16px; font-size: 0.8rem; color: var(--text-secondary); background: rgba(148, 163, 184, 0.1); border: 1px solid rgba(148, 163, 184, 0.2); padding: 8px 14px; border-radius: 8px;">⏭️ <strong>Clarification Skipped:</strong> Showing best-available shortlist.</div>`;
  } else if (totalMatches > 8) {
    statusBannerHtml = `<div style="margin-bottom: 16px; font-size: 0.8rem; color: #fbbf24; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); padding: 8px 14px; border-radius: 8px;">⚡ <strong>Shortlist Cap Enforced:</strong> Showing top 8 relevance-ranked candidates out of ${totalMatches} matching photos.</div>`;
  }

  if (statusBannerHtml) {
    const bannerWrapper = document.createElement('div');
    bannerWrapper.innerHTML = statusBannerHtml;
    container.appendChild(bannerWrapper);
  }

  const gridEl = document.createElement('div');
  gridEl.className = 'shortlist-grid';

  results.forEach((item, index) => {
    const card = createShortlistCard(item, index + 1);
    gridEl.appendChild(card);
  });

  container.appendChild(gridEl);
}

// Create Shortlist Card Component
function createShortlistCard(item, rankNum) {
  const photo = item.photo;
  const card = document.createElement('div');
  card.className = 'shortlist-card';

  const rankOverlay = document.createElement('div');
  rankOverlay.className = 'rank-badge-overlay';
  rankOverlay.textContent = `#${rankNum}`;
  card.appendChild(rankOverlay);

  const img = document.createElement('img');
  img.className = 'shortlist-thumb';
  img.src = photo.image_url;
  img.alt = photo.photo_id;

  const info = document.createElement('div');
  info.className = 'shortlist-info';

  const topRow = document.createElement('div');
  topRow.className = 'shortlist-top-row';

  const title = document.createElement('div');
  title.className = 'shortlist-title';
  title.textContent = getPhotoTitle(photo);

  const confBadge = document.createElement('span');
  if (state.searchMode === 'literal') {
    confBadge.className = 'confidence-pill confidence-literal';
    confBadge.textContent = 'Literal Match';
  } else if (item.confidence === 'High Match') {
    confBadge.className = 'confidence-pill confidence-high';
    confBadge.textContent = 'High Match';
  } else {
    confBadge.className = 'confidence-pill confidence-medium';
    confBadge.textContent = 'Medium Match';
  }

  topRow.appendChild(title);
  topRow.appendChild(confBadge);

  const metaDate = document.createElement('div');
  metaDate.className = 'photo-meta';
  metaDate.textContent = `Taken: ${photo.approx_date_range}`;

  const whyBox = document.createElement('div');
  whyBox.className = 'why-matched-box';
  whyBox.innerHTML = `
    <div class="why-matched-label">Why This Matched</div>
    <div>${item.explanation}</div>
  `;

  info.appendChild(topRow);
  info.appendChild(metaDate);
  info.appendChild(whyBox);

  card.appendChild(img);
  card.appendChild(info);

  card.addEventListener('click', () => openLightbox(photo));
  return card;
}

// Render Structured Empty State Card
function renderEmptyState(query) {
  const container = document.getElementById('viewContainer');
  container.innerHTML = `
    <div class="empty-state-card">
      <div class="empty-state-icon">🔎</div>
      <div class="empty-state-title">No Strong Matches Found</div>
      <div class="empty-state-desc">
        We couldn't find any photos matching "<strong>${escapeHtml(query)}</strong>".<br>
        Try describing the relationship, location, or purpose rather than specific names.
      </div>
      <div class="empty-state-hints">
        <span class="hint-chip" onclick="applySearchHint('photo with my roommate at the café')">"roommate at the café"</span>
        <span class="hint-chip" onclick="applySearchHint('receipt for my laptop')">"receipt for laptop"</span>
        <span class="hint-chip" onclick="applySearchHint('birthday cake')">"birthday cake"</span>
        <span class="hint-chip" onclick="applySearchHint('photo from a trip')">"photo from a trip"</span>
      </div>
    </div>
  `;
}

// Global Search Hint Trigger
window.applySearchHint = function(hintText) {
  const searchInput = document.getElementById('searchInput');
  searchInput.value = hintText;
  document.getElementById('clearSearchBtn').style.display = 'block';
  performSearch(hintText);
};

// Create Standard Library Photo Card
function createStandardPhotoCard(photo) {
  const card = document.createElement('div');
  card.className = 'photo-card';

  const img = document.createElement('img');
  img.className = 'photo-thumb';
  img.src = photo.image_url;
  img.alt = photo.photo_id;

  const info = document.createElement('div');
  info.className = 'photo-info';

  const title = document.createElement('div');
  title.className = 'photo-title';
  title.textContent = getPhotoTitle(photo);

  const meta = document.createElement('div');
  meta.className = 'photo-meta';
  const relBadge = photo.relationships.length ? ` • <span style="color: var(--accent-primary); font-weight: 500;">${photo.relationships.join(', ')}</span>` : '';
  meta.innerHTML = `${photo.approx_date_range}${relBadge}`;

  info.appendChild(title);
  info.appendChild(meta);
  card.appendChild(img);
  card.appendChild(info);

  card.addEventListener('click', () => openLightbox(photo));
  return card;
}

// Group photos by approx_date_range
function groupPhotosByDate(photos) {
  const customOrder = [
    "Fall 2024",
    "Summer 2024",
    "Spring 2024",
    "Winter 2024",
    "Fall 2023",
    "Spring 2023"
  ];

  const groups = {};
  photos.forEach(p => {
    const dateLabel = p.approx_date_range || 'Other Photos';
    if (!groups[dateLabel]) groups[dateLabel] = [];
    groups[dateLabel].push(p);
  });

  const sortedGroups = {};
  customOrder.forEach(orderKey => {
    if (groups[orderKey]) {
      sortedGroups[orderKey] = groups[orderKey];
    }
  });

  for (const k in groups) {
    if (!sortedGroups[k]) {
      sortedGroups[k] = groups[k];
    }
  }

  return sortedGroups;
}

// Open Lightbox Detail View
function openLightbox(photo) {
  state.selectedPhoto = photo;
  document.getElementById('lightboxImg').src = photo.image_url;
  document.getElementById('lightboxTitle').textContent = getPhotoTitle(photo);
  document.getElementById('lightboxDate').textContent = `Taken: ${new Date(photo.date_taken).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })} (${photo.approx_date_range})`;

  const metaBox = document.getElementById('lightboxMetaFields');
  
  const relHtml = photo.relationships.length 
    ? photo.relationships.map(r => `<span class="meta-tag">${r}</span>`).join('') 
    : '<span style="color: var(--text-muted);">None tagged</span>';
    
  const namesHtml = photo.tagged_names.length 
    ? photo.tagged_names.map(n => `<span class="meta-tag">${n}</span>`).join('') 
    : '<span style="color: var(--text-muted);">None</span>';

  const tagsHtml = photo.event_tags.length 
    ? photo.event_tags.map(t => `<span class="meta-tag">${t}</span>`).join('') 
    : '<span style="color: var(--text-muted);">None</span>';

  metaBox.innerHTML = `
    <div class="meta-field-item">
      <div class="meta-field-label">Relationships</div>
      <div class="meta-field-value">${relHtml}</div>
    </div>
    <div class="meta-field-item">
      <div class="meta-field-label">Tagged Names</div>
      <div class="meta-field-value">${namesHtml}</div>
    </div>
    <div class="meta-field-item">
      <div class="meta-field-label">Place Name</div>
      <div class="meta-field-value">${photo.place_name ? `📍 ${photo.place_name}` : '<em style="color: var(--text-muted);">Unnamed / Null (Visuals Only)</em>'}</div>
    </div>
    <div class="meta-field-item">
      <div class="meta-field-label">Visual Descriptors</div>
      <div class="meta-field-value">${photo.visual_descriptors.map(v => `<span class="meta-tag" style="background: rgba(255, 255, 255, 0.05); color: var(--text-secondary); border-color: var(--surface-border);">${v}</span>`).join('')}</div>
    </div>
    <div class="meta-field-item">
      <div class="meta-field-label">Event Tags</div>
      <div class="meta-field-value">${tagsHtml}</div>
    </div>
    <div class="meta-field-item">
      <div class="meta-field-label">Document Purpose</div>
      <div class="meta-field-value">${photo.document_purpose ? `<span style="color: #2dd4bf; font-weight: 500;">📄 ${photo.document_purpose}</span>` : '<span style="color: var(--text-muted);">N/A (Standard Photo)</span>'}</div>
    </div>
    <div class="meta-field-item">
      <div class="meta-field-label">OCR Text</div>
      <div class="meta-field-value">${photo.ocr_text ? `<div class="ocr-box">${photo.ocr_text}</div>` : '<span style="color: var(--text-muted);">None (No printed text)</span>'}</div>
    </div>
  `;

  const lightbox = document.getElementById('lightbox');
  lightbox.classList.add('active');
  lightbox.setAttribute('aria-hidden', 'false');
}

// Close Lightbox
function closeLightbox() {
  const lightbox = document.getElementById('lightbox');
  lightbox.classList.remove('active');
  lightbox.setAttribute('aria-hidden', 'true');
  state.selectedPhoto = null;
}

// Utility: Escape HTML
function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
