const API_BASE = '/api/v1';
let currentFileId = null;
let currentOutputId = null;
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const profileSection = document.getElementById('profile-section');
const cleanSection = document.getElementById('clean-section');
const resultsSection = document.getElementById('results-section');
const profileResults = document.getElementById('profile-results');
const cleanResults = document.getElementById('clean-results');
const cleanBtn = document.getElementById('clean-btn');
const downloadBtn = document.getElementById('download-btn');
const resetBtn = document.getElementById('reset-btn');
const aggressiveMode = document.getElementById('aggressive-mode');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loading-text');
const errorAlert = document.getElementById('error-alert');
const errorMessage = document.getElementById('error-message');
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('drag-over'); });
uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.classList.remove('drag-over'); const files = e.dataTransfer.files; if (files.length > 0) { fileInput.files = files; handleFileSelect(); } });
async function handleFileSelect() { const file = fileInput.files[0]; if (!file) return; fileInfo.innerHTML = '<span class="icon">📄</span><div><strong>' + file.name + '</strong><div style="color: var(--text-light); font-size: 0.875rem;">' + formatBytes(file.size) + '</div></div>'; fileInfo.classList.remove('hidden'); await uploadFile(file); }
async function uploadFile(file) { showLoading('Uploading file...'); const formData = new FormData(); formData.append('file', file); try { const response = await fetch(API_BASE + '/upload', { method: 'POST', body: formData }); if (!response.ok) throw new Error('Upload failed'); const data = await response.json(); currentFileId = data.file_id; hideLoading(); await profileData(); } catch (error) { hideLoading(); showError('Failed to upload file: ' + error.message); } }
async function profileData() { showLoading('Analyzing data quality...'); try { const response = await fetch(API_BASE + '/profile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ file_id: currentFileId }) }); if (!response.ok) throw new Error('Profiling failed'); const data = await response.json(); hideLoading(); displayProfile(data); } catch (error) { hideLoading(); showError('Failed to profile data: ' + error.message); } }
function displayProfile(data) { const score = data.overall_quality_score; const scoreColor = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--error)'; profileResults.innerHTML = '<div class="quality-score" style="background: ' + scoreColor + ';"><span>📊</span><span>' + score + '/100</span><span style="font-size: 1rem; font-weight: normal;">Quality Score</span></div><div class="stats-grid"><div class="stat-box"><div class="value">' + data.rows + '</div><div class="label">Rows</div></div><div class="stat-box"><div class="value">' + data.columns + '</div><div class="label">Columns</div></div><div class="stat-box"><div class="value">' + data.issues_found.length + '</div><div class="label">Issues Found</div></div></div>'; profileSection.classList.remove('hidden'); cleanSection.classList.remove('hidden'); }
cleanBtn.addEventListener('click', async () => { showLoading('Cleaning your data...'); try { const response = await fetch(API_BASE + '/clean', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ file_id: currentFileId, aggressive: aggressiveMode.checked }) }); if (!response.ok) throw new Error('Cleaning failed'); const data = await response.json(); currentOutputId = data.output_file_id; hideLoading(); displayResults(data); } catch (error) { hideLoading(); showError('Failed to clean data: ' + error.message); } });
function displayResults(data) { const improvement = data.quality_score_after - data.quality_score_before; const improvementText = improvement > 0 ? '<span style="color: var(--success);">+' + improvement.toFixed(1) + '</span>' : improvement < 0 ? '<span style="color: var(--error);">' + improvement.toFixed(1) + '</span>' : '<span>No change</span>'; cleanResults.innerHTML = '<div class="stats-grid"><div class="stat-box"><div class="value">' + data.rows_after + '</div><div class="label">Final Rows</div></div><div class="stat-box"><div class="value">' + (data.rows_before - data.rows_after) + '</div><div class="label">Rows Removed</div></div><div class="stat-box"><div class="value">' + improvementText + '</div><div class="label">Quality Improvement</div></div></div><div class="operations-list"><h3>🔧 Operations Performed</h3><ul>' + data.operations_performed.map(op => '<li>' + op + '</li>').join('') + '</ul></div><div style="background: #d1fae5; padding: 1rem; border-radius: 8px; text-align: center;"><strong style="color: #065f46;">✅ Your data is now clean and ready to download!</strong></div>'; resultsSection.classList.remove('hidden'); resultsSection.scrollIntoView({ behavior: 'smooth' }); }
downloadBtn.addEventListener('click', async () => { try { const response = await fetch(API_BASE + '/download/' + currentOutputId + '?output=true'); if (!response.ok) throw new Error('Download failed'); const blob = await response.blob(); const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'cleaned_data_' + currentOutputId + '.csv'; document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); document.body.removeChild(a); } catch (error) { showError('Failed to download file: ' + error.message); } });
resetBtn.addEventListener('click', () => { location.reload(); });
function showLoading(text) { loadingText.textContent = text; loading.classList.remove('hidden'); }
function hideLoading() { loading.classList.add('hidden'); }
function showError(message) { errorMessage.textContent = message; errorAlert.classList.remove('hidden'); setTimeout(() => { errorAlert.classList.add('hidden'); }, 5000); }
function formatBytes(bytes) { if (bytes === 0) return '0 Bytes'; const k = 1024; const sizes = ['Bytes', 'KB', 'MB', 'GB']; const i = Math.floor(Math.log(bytes) / Math.log(k)); return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]; }
