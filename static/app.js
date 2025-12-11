var currentPath = "";
var sortField = null;
var sortDirection = 'asc';
var rowsCache = [];
var editingFileId = null;

function formatPath(p) {
  if (!p) return '';
  return p.replace(/\/+/g, '/').replace(/^\/|\/$/g, '');
}
function formatSize(bytes) {
  if (bytes === null || bytes === undefined) return '—';
  var units = ['B','KB','MB','GB','TB'];
  var v = Number(bytes);
  var i = 0;
  while (v >= 1024 && i < units.length-1) { v = v/1024; i++; }
  return Math.round(v*10)/10 + ' ' + units[i];
}
function fmtDate(s) {
  if (!s) return '';
  var d = new Date(s);
  if (isNaN(d)) return s;
  function pad(n){ return (n<10? '0':'') + n; }
  return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
}
function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

async function load(path) {
  if (typeof path === 'undefined') path = '';
  currentPath = formatPath(path);
  var url = '/api/contents?path=' + encodeURIComponent(currentPath);
  var res;
  try {
    res = await fetch(url);
  } catch (e) {
    console.error('Fetch failed', e);
    goBack();
    return;
  }
  if (!res || !res.ok) { goBack(); return; }
  var data;
  try { data = await res.json(); } catch (e) { goBack(); return; }
  if (!data || data.status !== 'ok') { goBack(); return; }

  document.getElementById('pathDisplay').textContent = '/' + currentPath;

  rowsCache = [];
  var i;
  var dirs = data.directories || [];
  for (i = 0; i < dirs.length; i++) {
    rowsCache.push({ type: 'dir', name: dirs[i], icon: '📁', size: null, comment: '', created: '', updated: '' });
  }
  var files = data.files || [];
  for (i = 0; i < files.length; i++) {
    var f = files[i];
    rowsCache.push({ type: 'file', id: f.id, name: (f.name || '') + '.' + (f.extension || ''), rawName: f.name, ext: f.extension, icon: '📄', size: f.size, comment: f.comment || '', created: f.created_at, updated: f.updated_at });
  }

  renderTable();
}

function compareGeneric(a,b,field) {
  var va = (a[field] === undefined || a[field] === null) ? '' : a[field];
  var vb = (b[field] === undefined || b[field] === null) ? '' : b[field];
  if (field === 'size') return (Number(va) || 0) - (Number(vb) || 0);
  if (field === 'created' || field === 'updated') return (Date.parse(va) || 0) - (Date.parse(vb) || 0);
  if (field === 'name') return String((a.rawName || a.name)).toLowerCase().localeCompare(String((b.rawName || b.name)).toLowerCase());
  return String(va).toLowerCase().localeCompare(String(vb).toLowerCase());
}

function renderTable() {
  var tbody = document.getElementById('tbody');
  tbody.innerHTML = '';
  var rows = rowsCache.slice();

  if (rows.length === 0) {
    var tr = document.createElement('tr');
    var td = document.createElement('td');
    td.colSpan = 7;
    td.className = 'empty-msg';
    td.textContent = 'Эта папка пуста.';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  if (sortField) {
    rows.sort(function(a,b){
      if (sortField !== 'type' && a.type !== b.type) return a.type === 'dir' ? -1 : 1;
      var cmp = compareGeneric(a,b,sortField);
      return sortDirection === 'asc' ? cmp : -cmp;
    });
    if (sortField === 'type') {
      rows.sort(function(a,b){ return sortDirection === 'asc' ? (a.type === 'dir' ? -1 : 1) : (a.type === 'dir' ? 1 : -1); });
    }
  } else {
    rows.sort(function(a,b){ return a.type === b.type ? 0 : (a.type === 'dir' ? -1 : 1); });
  }

  for (var ri = 0; ri < rows.length; ri++) {
    var item = rows[ri];
    var tr = document.createElement('tr');

    var tdName = document.createElement('td');
    tdName.innerHTML = '<span class="icon">' + item.icon + '</span> ' + escapeHtml(item.name);
    if (item.type === 'dir') {
      tr.onclick = (function(it){ return function(){ var newPath = currentPath ? currentPath + '/' + it.name : it.name; load(newPath.replace(/\/+$/,'')); }; })(item);
    } else {
      tr.onclick = (function(it){ return function(){ window.location = '/api/files/' + it.id + '/download'; }; })(item);
    }

    var tdType = document.createElement('td'); tdType.textContent = item.type === 'dir' ? 'Папка' : 'Файл';
    var tdSize = document.createElement('td'); tdSize.textContent = (item.size !== null && item.size !== undefined) ? formatSize(item.size) : '—';
    var tdComment = document.createElement('td'); tdComment.textContent = item.comment || '';
    var tdCreated = document.createElement('td'); tdCreated.textContent = fmtDate(item.created);
    var tdUpdated = document.createElement('td'); tdUpdated.textContent = fmtDate(item.updated);

    var tdActions = document.createElement('td'); tdActions.className = 'actions-cell'; tdActions.style.width = '140px';
    if (item.type === 'file') {
      tdActions.innerHTML = '<span class="file-action delete" title="Удалить" onclick="event.stopPropagation(); deleteFile(' + item.id + ')">✖</span>' +
                            '<span class="file-action" title="Переименовать" onclick="event.stopPropagation(); openEditModal(' + item.id + ')">✏️</span>';
    }

    tr.appendChild(tdName);
    tr.appendChild(tdType);
    tr.appendChild(tdSize);
    tr.appendChild(tdComment);
    tr.appendChild(tdCreated);
    tr.appendChild(tdUpdated);
    tr.appendChild(tdActions);

    tbody.appendChild(tr);
  }
}

function deleteFile(id){ if (!confirm('Удалить файл?')) return; fetch('/api/files/' + id, { method: 'DELETE' }).then(function(){ load(currentPath); }).catch(function(){ alert('Ошибка при удалении'); }); }

function openAddModal(){ document.getElementById('addModal').classList.remove('hidden'); document.getElementById('addModal').setAttribute('aria-hidden','false'); document.getElementById('addPath').value = currentPath || ''; document.getElementById('addComment').value = ''; }
function closeAddModal(){ document.getElementById('addModal').classList.add('hidden'); document.getElementById('addModal').setAttribute('aria-hidden','true'); document.getElementById('addFileInput').value = ''; }
async function confirmAddFile(){
  var input = document.getElementById('addFileInput');
  if (!input.files || input.files.length === 0) { alert('Выберите файл'); return; }
  var file = input.files[0];

  var form = new FormData();
  form.append('path', formatPath(document.getElementById('addPath').value || currentPath));
  form.append('comment', document.getElementById('addComment').value || '');
  form.append('files', file);

  var res;
  try {
    res = await fetch('/api/files', { method: 'POST', body: form });
  } catch (e) {
    alert('Ошибка сети');
    return;
  }

  var j = {};
  try { j = await res.json(); } catch(e) {}

  if (res.ok && j.status === 'ok') {
    closeAddModal();
    load(currentPath);
  } else {
    console.warn('Server response:', j);
    alert(j.msg || 'Ошибка, но загрузка могла пройти.');
  }
}

function openEditModal(id){ var file = null; for(var i=0;i<rowsCache.length;i++){ if(rowsCache[i].type==='file' && rowsCache[i].id===id){ file = rowsCache[i]; break; } } if(!file) return; editingFileId = id; document.getElementById('editName').value = file.rawName || file.name.replace(/\.[^.]+$/, ''); document.getElementById('editPath').value = file.path || currentPath; document.getElementById('editComment').value = file.comment || ''; document.getElementById('editModal').classList.remove('hidden'); document.getElementById('editModal').setAttribute('aria-hidden','false'); }
function closeEditModal(){ document.getElementById('editModal').classList.add('hidden'); document.getElementById('editModal').setAttribute('aria-hidden','true'); editingFileId = null; }
async function confirmEditFile(){ if(!editingFileId) return; var name = document.getElementById('editName').value.trim(); var path = document.getElementById('editPath').value.trim(); var comment = document.getElementById('editComment').value.trim(); if(!name){ alert('Имя не может быть пустым'); return; } var form = new FormData(); form.append('name', name); form.append('path', path); form.append('comment', comment); var res = await fetch('/api/files/' + editingFileId, { method: 'PUT', body: form }); var j = await res.json(); if (j && j.status === 'ok') { closeEditModal(); load(currentPath); } else { alert((j && j.msg) ? j.msg : 'Ошибка при сохранении'); } }

window.addEventListener('DOMContentLoaded', function(){ var map = { 'Имя':'name', 'Тип':'type', 'Размер':'size', 'Комментарий':'comment', 'Создан':'created', 'Обновлён':'updated' }; var ths = document.querySelectorAll('thead th'); for(var i=0;i<ths.length;i++){ (function(th){ th.addEventListener('click', function(){ var txt = th.textContent.trim(); var f = map[txt]; if(!f) return; if(sortField===f) sortDirection = (sortDirection==='asc') ? 'desc' : 'asc'; else { sortField = f; sortDirection = 'asc'; } renderTable(); }); })(ths[i]); } // bind modal confirm buttons

});

function goBack(){ if(!currentPath) return; var parts = currentPath.split('/').filter(function(x){ return x; }); parts.pop(); load(parts.join('/')); }

// Применить сохранённую тему при загрузке
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark");
    }
});

// Переключение темы по кнопке
document.getElementById("themeToggle").addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
});

load();
