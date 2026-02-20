// ===== API Base URL =====
var API = "";

// ===== Tab Switching =====
function switchTab(tabName) {
    // Hide all tab contents
    var contents = document.querySelectorAll(".tab-content");
    for (var i = 0; i < contents.length; i++) {
        contents[i].classList.remove("active");
    }

    // Deactivate all nav links
    var navLinks = document.querySelectorAll(".nav-link");
    for (var i = 0; i < navLinks.length; i++) {
        navLinks[i].classList.remove("active");
    }

    // Show the selected tab
    document.getElementById("tab-" + tabName).classList.add("active");

    // Activate the clicked nav link
    var links = document.querySelectorAll(".nav-link");
    for (var i = 0; i < links.length; i++) {
        if (links[i].textContent.toLowerCase().indexOf(tabName === "chat" ? "ask" : tabName) >= 0) {
            links[i].classList.add("active");
        }
    }

    // Refresh data when switching tabs
    if (tabName === "dashboard") loadStats();
    if (tabName === "documents") loadDocuments();
    if (tabName === "chat") loadDocSelect();
}


// ===== Stats =====
function loadStats() {
    fetch(API + "/api/documents")
        .then(function (res) { return res.json(); })
        .then(function (docs) {
            var totalDocs = docs.length;
            var totalSummaries = 0;
            var totalChunks = 0;

            for (var i = 0; i < docs.length; i++) {
                if (docs[i].summary) totalSummaries++;
                totalChunks += docs[i].chunks || 0;
            }

            document.getElementById("statDocs").textContent = totalDocs;
            document.getElementById("statSummaries").textContent = totalSummaries;
            document.getElementById("statChunks").textContent = totalChunks > 1000 ? (totalChunks / 1000).toFixed(1) + "K" : totalChunks;

            // Show recent docs on dashboard
            var recentSection = document.getElementById("recentDocsSection");
            var recentDocs = document.getElementById("recentDocs");
            if (docs.length > 0) {
                recentSection.style.display = "block";
                var html = "";
                var recent = docs.slice(-3).reverse();
                for (var i = 0; i < recent.length; i++) {
                    var doc = recent[i];
                    var date = new Date(doc.uploaded_at).toLocaleDateString();
                    html += '<div class="doc-item">';
                    html += '  <div class="doc-info">';
                    html += '    <h3>📄 ' + doc.title + '</h3>';
                    html += '    <span class="doc-meta">' + doc.pages + ' pages &bull; ' + doc.chunks + ' chunks &bull; ' + date + '</span>';
                    html += '  </div>';
                    html += '  <div class="doc-actions">';
                    html += '    <button class="btn btn-primary" onclick="viewSummary(\'' + doc.id + '\', \'' + doc.title.replace(/'/g, "\\'") + '\')">View Summary</button>';
                    html += '    <button class="btn btn-outline" onclick="askAboutDoc(\'' + doc.id + '\')">Ask Question</button>';
                    html += '    <button class="btn btn-danger" onclick="deleteDoc(\'' + doc.id + '\', \'' + doc.title.replace(/'/g, "\\'") + '\')">Delete</button>';
                    html += '  </div>';
                    html += '</div>';
                }
                recentDocs.innerHTML = html;
            } else {
                recentSection.style.display = "none";
            }
        });
}


// ===== File Upload =====
var dropZone = document.getElementById("dropZone");
var fileInput = document.getElementById("fileInput");
var uploadStatus = document.getElementById("uploadStatus");

dropZone.addEventListener("click", function () {
    fileInput.click();
});

fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        uploadFile(fileInput.files[0]);
    }
});

dropZone.addEventListener("dragover", function (e) {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", function (e) {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
        uploadFile(e.dataTransfer.files[0]);
    }
});

function uploadFile(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
        showStatus("Only PDF files are supported.", "error");
        return;
    }

    showStatus('Uploading and processing "' + file.name + '"... This may take a moment.', "loading");

    var formData = new FormData();
    formData.append("file", file);

    fetch(API + "/api/upload", {
        method: "POST",
        body: formData
    })
        .then(function (res) {
            if (!res.ok) {
                // Return a special object if the response is not 200 OK
                return res.text().then(function (text) {
                    throw new Error("Server returned " + res.status + ": " + (text.slice(0, 50) || "Empty response"));
                });
            }
            return res.json();
        })
        .then(function (data) {
            if (data.error) {
                showStatus("Error: " + data.error, "error");
            } else {
                showStatus('✅ "' + data.title + '" uploaded and indexed successfully!', "success");
                fileInput.value = "";
                loadStats();
            }
        })
        .catch(function (err) {
            showStatus("Upload failed: " + err.message, "error");
            console.error("Upload error details:", err);
        });
}

function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = "status-message " + type;
    uploadStatus.classList.remove("hidden");
}


// ===== Documents List =====
function loadDocuments() {
    var docList = document.getElementById("docList");

    fetch(API + "/api/documents")
        .then(function (res) { return res.json(); })
        .then(function (docs) {
            if (docs.length === 0) {
                docList.innerHTML = '<p class="empty-state">No documents uploaded yet. Go to Dashboard to upload one!</p>';
                return;
            }

            var html = "";
            for (var i = 0; i < docs.length; i++) {
                var doc = docs[i];
                var date = new Date(doc.uploaded_at).toLocaleDateString();
                html += '<div class="doc-item">';
                html += '  <div class="doc-info">';
                html += '    <h3>📄 ' + doc.title + '</h3>';
                html += '    <span class="doc-meta">' + doc.pages + ' pages &bull; ' + doc.chunks + ' chunks &bull; Uploaded ' + date + '</span>';
                html += '  </div>';
                html += '  <div class="doc-actions">';
                html += '    <button class="btn btn-primary" onclick="viewSummary(\'' + doc.id + '\', \'' + doc.title.replace(/'/g, "\\'") + '\')">View Summary</button>';
                html += '    <button class="btn btn-outline" onclick="askAboutDoc(\'' + doc.id + '\')">Ask Question</button>';
                html += '    <button class="btn btn-danger" onclick="deleteDoc(\'' + doc.id + '\', \'' + doc.title.replace(/'/g, "\\'") + '\')">Delete</button>';
                html += '  </div>';
                html += '</div>';
            }
            docList.innerHTML = html;
        })
        .catch(function () {
            docList.innerHTML = '<p class="empty-state">Failed to load documents.</p>';
        });
}


// ===== Summary Modal =====
function viewSummary(docId, title) {
    var modal = document.getElementById("summaryModal");
    var modalTitle = document.getElementById("modalTitle");
    var modalBody = document.getElementById("modalBody");

    modalTitle.textContent = title + " — Summary";
    modalBody.innerHTML = '<div class="loader">⏳ Generating summary... This may take a moment.</div>';
    modal.classList.remove("hidden");

    fetch(API + "/api/summary/" + docId)
        .then(function (res) {
            if (!res.ok) {
                throw new Error("Server returned " + res.status);
            }
            return res.text();
        })
        .then(function (text) {
            if (!text || !text.trim()) {
                throw new Error("Empty response from server — try again in a moment.");
            }
            var data = JSON.parse(text);
            if (data.error) {
                modalBody.textContent = "Error: " + data.error;
            } else {
                modalBody.textContent = data.summary;
            }
        })
        .catch(function (err) {
            modalBody.textContent = "Failed to generate summary: " + err.message;
        });
}

function closeSummaryModal() {
    document.getElementById("summaryModal").classList.add("hidden");
}


// ===== Delete Document =====
function deleteDoc(docId, title) {
    if (!confirm('Delete "' + title + '"? This cannot be undone.')) return;

    fetch(API + '/api/documents/' + docId, { method: 'DELETE' })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                loadStats();
                loadDocuments();
            }
        })
        .catch(function (err) {
            alert('Delete failed: ' + err.message);
        });
}


// ===== Ask About Document (jump to chat with doc pre-selected) =====
function askAboutDoc(docId) {
    switchTab('chat');
    loadDocSelect();
    // Wait for dropdown to populate then select the doc
    setTimeout(function () {
        document.getElementById('docSelect').value = docId;
        document.getElementById('questionInput').focus();
    }, 300);
}


// ===== Chat / Query =====
function loadDocSelect() {
    var select = document.getElementById("docSelect");
    var currentVal = select.value;

    fetch(API + "/api/documents")
        .then(function (res) { return res.json(); })
        .then(function (docs) {
            select.innerHTML = '<option value="">All Documents</option>';
            for (var i = 0; i < docs.length; i++) {
                var opt = document.createElement("option");
                opt.value = docs[i].id;
                opt.textContent = docs[i].title;
                select.appendChild(opt);
            }
            select.value = currentVal;
        });
}

function sendQuestion() {
    var input = document.getElementById("questionInput");
    var question = input.value.trim();
    if (!question) return;

    var docId = document.getElementById("docSelect").value;

    addMessage(question, "user");
    input.value = "";

    var loadingId = addMessage("Thinking...", "bot");
    document.getElementById("sendBtn").disabled = true;

    var body = { question: question };
    if (docId) body.doc_id = docId;

    fetch(API + "/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            var loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();

            if (data.error) {
                addMessage("Error: " + data.error, "bot");
            } else {
                addMessage(data.answer, "bot", data.sources);
            }
            document.getElementById("sendBtn").disabled = false;
        })
        .catch(function (err) {
            var loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();
            addMessage("Something went wrong: " + err.message, "bot");
            document.getElementById("sendBtn").disabled = false;
        });
}

var messageCounter = 0;

function addMessage(text, sender, sources) {
    var chatMessages = document.getElementById("chatMessages");
    var msgId = "msg-" + (++messageCounter);

    var div = document.createElement("div");
    div.className = "message " + (sender === "user" ? "user-message" : "bot-message");
    div.id = msgId;

    var avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "user" ? "👤" : "🤖";

    var textDiv = document.createElement("div");
    textDiv.className = "message-text";
    textDiv.textContent = text;

    if (sources && sources.length > 0) {
        var sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources";

        var details = document.createElement("details");
        var summary = document.createElement("summary");
        summary.textContent = "📎 View source excerpts (" + sources.length + ")";
        details.appendChild(summary);

        for (var i = 0; i < sources.length; i++) {
            var chunk = document.createElement("div");
            chunk.className = "source-chunk";
            chunk.textContent = sources[i].substring(0, 200) + "...";
            details.appendChild(chunk);
        }

        sourcesDiv.appendChild(details);
        textDiv.appendChild(sourcesDiv);
    }

    div.appendChild(avatar);
    div.appendChild(textDiv);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return msgId;
}

// Send on Enter key
document.getElementById("questionInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendQuestion();
});

// Close modal on Escape
document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSummaryModal();
});

// Load stats on page load
loadStats();
