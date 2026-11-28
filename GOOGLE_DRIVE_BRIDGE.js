/**
 * =============================================================================
 * MASTER GOOGLE APPS SCRIPT: DRIVE BRIDGE + AUTOMATIC WORKFLOW TRIGGERS
 * Faraz Sir's Multi-Channel Cloud Engine (Shadow Will + GTA + Chronicle Vault)
 * Repository: ashrafnadim47-creator/flintgrit-cloud-engine
 * =============================================================================
 * 
 * KAISE SETUP KAREIN (Only 2 Minutes):
 * 1. https://script.google.com open kijiye aur New Project banaiye.
 * 2. Purana sab hata kar ye poora code paste kar dijiye.
 * 3. File save kijiye (Ctrl + S).
 * 4. Dropdown se 'setupAllDailyTriggers' select karke 'Run' daba dijiye (ek bar permission allow karein).
 *    -> Isse 1:00 PM GTA, 7:00 PM Shadow Will, aur Subah History Shorts ke triggers automatic lag jayenge!
 * 5. Upar 'Deploy' -> 'New deployment' par click kijiye:
 *    - Type: 'Web app'
 *    - Execute as: 'Me'
 *    - Who has access: 'Anyone' (IMPORTANT: Anyone zaroor select karein!)
 * 6. 'Deploy' dabayein aur jo Web App URL (ends in /exec) mile, use copy karke
 *    GitHub Secrets me 'DRIVE_BRIDGE_URL' me paste kar dijiye.
 * =============================================================================
 */

const GITHUB_TOKEN = "PASTE_YOUR_GITHUB_TOKEN_HERE"; // Faraz Sir: Paste your GitHub token here
const REPO = "ashrafnadim47-creator/flintgrit-cloud-engine";

const DOC_FOLDER_ID = "1KfsTib0zr1vRYJc_xEXjNod8hyReCa0e"; // Documentary_Auto folder
const HISTORY_FOLDER_NAME = "HistoryShorts_Auto";

// =============================================================================
// 1. GITHUB WORKFLOW TRIGGERS (Zero delay, exact time trigger)
// =============================================================================

function triggerWorkflow(workflowFile, inputs) {
  const url = "https://api.github.com/repos/" + REPO + "/actions/workflows/" + workflowFile + "/dispatches";
  const payload = { ref: "main" };
  if (inputs) {
    payload.inputs = inputs;
  }
  const options = {
    method: "post",
    headers: {
      "Authorization": "Bearer " + GITHUB_TOKEN,
      "Accept": "application/vnd.github+json",
      "User-Agent": "Google-Apps-Script-Cloud-Trigger"
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  try {
    const response = UrlFetchApp.fetch(url, options);
    Logger.log(workflowFile + " response code: " + response.getResponseCode() + " | " + response.getContentText());
    return response.getResponseCode();
  } catch (err) {
    Logger.log("Error triggering " + workflowFile + ": " + err);
    return 500;
  }
}

// 1. Dopahar 1:00 PM IST (Vice City Pulse - GTA Shorts ~40s)
function triggerViceCityPulse() {
  Logger.log("Triggering Vice City Pulse GTA Short...");
  triggerWorkflow("channel2_vice_city_pulse.yml");
}

// 2. Shaam 7:00 PM IST (Shadow Will - Merged 3D+2D Ultra Quality Short)
function triggerShadowWill() {
  Logger.log("Triggering Shadow Will 3D+2D Short...");
  triggerWorkflow("channel1_shadow_will_unified.yml", { format: "short" });
}

// 3. Subah 8:25 AM & 9:15 AM IST (Chronicle Vault - History Shorts)
function triggerHistoryShorts() {
  Logger.log("Triggering Daily History Shorts Pipeline...");
  triggerWorkflow("daily_history_shorts.yml");
}

// 4. Shaam 5:00 PM IST (Chronicle Vault - AI Geek Documentary)
function triggerDocumentary() {
  Logger.log("Triggering AI Geek Documentary...");
  triggerWorkflow("daily_documentary.yml");
}

// =============================================================================
// 2. ONE-CLICK AUTO TRIGGER SETUP / RESET
// =============================================================================

/**
 * Ye function run karne se sabhi purane duplicate triggers delete ho jayenge
 * aur ekdum naye time par perfect daily triggers automatically set ho jayenge!
 */
function setupAllDailyTriggers() {
  // Pehle sabhi purane triggers clear karein
  removeAllTriggers();

  // 1. Vice City Pulse (GTA) - Dopahar 1:00 PM IST (13:00)
  ScriptApp.newTrigger("triggerViceCityPulse")
    .timeBased()
    .atHour(13)
    .nearMinute(0)
    .everyDays(1)
    .inTimezone("Asia/Kolkata")
    .create();

  // 2. Shadow Will (Merged 3D+2D) - Shaam 7:00 PM IST (19:00)
  ScriptApp.newTrigger("triggerShadowWill")
    .timeBased()
    .atHour(19)
    .nearMinute(0)
    .everyDays(1)
    .inTimezone("Asia/Kolkata")
    .create();

  // 3. History Shorts Run 1 (Voiceover generation) - Subah 8:25 AM IST
  ScriptApp.newTrigger("triggerHistoryShorts")
    .timeBased()
    .atHour(8)
    .nearMinute(25)
    .everyDays(1)
    .inTimezone("Asia/Kolkata")
    .create();

  // 4. History Shorts Run 2 (Video upload) - Subah 9:15 AM IST
  ScriptApp.newTrigger("triggerHistoryShorts")
    .timeBased()
    .atHour(9)
    .nearMinute(15)
    .everyDays(1)
    .inTimezone("Asia/Kolkata")
    .create();

  // 5. Documentary - Shaam 5:00 PM IST (17:00)
  ScriptApp.newTrigger("triggerDocumentary")
    .timeBased()
    .atHour(17)
    .nearMinute(0)
    .everyDays(1)
    .inTimezone("Asia/Kolkata")
    .create();

  Logger.log("SUCCESS! Sabhi 5 daily triggers set ho chuke hain (Asia/Kolkata timezone).");
}

/**
 * Agar kabhi sabhi triggers band karne ho, to ise run karein.
 */
function removeAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  Logger.log("Removed " + triggers.length + " triggers.");
}

// =============================================================================
// 3. GOOGLE DRIVE BRIDGE API (doGet & doPost)
// =============================================================================

function getFolder(folderIdOrName) {
  if (folderIdOrName) {
    try {
      return DriveApp.getFolderById(folderIdOrName);
    } catch (e) {}
  }
  const it = DriveApp.getFoldersByName(folderIdOrName);
  if (it.hasNext()) return it.next();
  return DriveApp.createFolder(folderIdOrName);
}

function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  try {
    const action = (e && e.parameter && e.parameter.action) || "list";

    // 1. LIST FILES IN SPECIFIED OR DEFAULT FOLDER
    if (action === "list") {
      const targetFolderId = (e && e.parameter && e.parameter.folderId) || DOC_FOLDER_ID;
      const folder = getFolder(targetFolderId);
      const files = folder.getFiles();
      const list = [];
      while (files.hasNext()) {
        const f = files.next();
        list.push({
          id: f.getId(),
          name: f.getName(),
          mimeType: f.getMimeType(),
          size: f.getSize()
        });
      }
      return jsonResponse({ success: true, files: list });
    }

    // 2. DOWNLOAD FILE AS BASE64 (BY ID OR BY NAME)
    if (action === "get_base64") {
      const fileId = e && e.parameter && e.parameter.id;
      if (fileId) {
        const f = DriveApp.getFileById(fileId);
        const b64 = Utilities.base64Encode(f.getBlob().getBytes());
        return jsonResponse({ success: true, name: f.getName(), base64: b64 });
      }
      const name = e.parameter.name;
      const targetFolderId = (e && e.parameter && e.parameter.folderId) || DOC_FOLDER_ID;
      const folder = getFolder(targetFolderId);
      const files = folder.getFilesByName(name);
      if (files.hasNext()) {
        const f = files.next();
        const b64 = Utilities.base64Encode(f.getBlob().getBytes());
        return jsonResponse({ success: true, name: name, base64: b64 });
      }
      return jsonResponse({ error: "File not found: " + name });
    }

    // 3. HISTORY SHORTS - GET PENDING SCRIPT.TXT
    if (action === "get_script") {
      const historyFolder = getFolder(HISTORY_FOLDER_NAME);
      const subfolders = historyFolder.getFolders();
      while (subfolders.hasNext()) {
        const sub = subfolders.next();
        if (sub.getName().indexOf("[UPLOADED]") !== -1) continue;
        const scriptFiles = sub.getFilesByName("script.txt");
        const mp3Files = sub.getFilesByName("voiceover.mp3");
        if (scriptFiles.hasNext() && !mp3Files.hasNext()) {
          const sf = scriptFiles.next();
          return jsonResponse({
            found: true,
            folderId: sub.getId(),
            folderName: sub.getName(),
            script: sf.getBlob().getDataAsString("UTF-8")
          });
        }
      }
      return jsonResponse({ found: false });
    }

    // 4. HISTORY SHORTS - GET PENDING FINAL_SHORT.MP4
    if (action === "get_mp4") {
      const historyFolder = getFolder(HISTORY_FOLDER_NAME);
      const subfolders = historyFolder.getFolders();
      while (subfolders.hasNext()) {
        const sub = subfolders.next();
        if (sub.getName().indexOf("[UPLOADED]") !== -1) continue;
        const mp4Files = sub.getFilesByName("final_short.mp4");
        if (mp4Files.hasNext()) {
          const mf = mp4Files.next();
          const metaFiles = sub.getFilesByName("metadata.json");
          let meta = {};
          if (metaFiles.hasNext()) {
            try {
              meta = JSON.parse(metaFiles.next().getBlob().getDataAsString("UTF-8"));
            } catch (err) {}
          }
          const b64 = Utilities.base64Encode(mf.getBlob().getBytes());
          return jsonResponse({
            found: true,
            folderId: sub.getId(),
            folderName: sub.getName(),
            mp4Base64: b64,
            metadata: meta
          });
        }
      }
      return jsonResponse({ found: false });
    }

    // PING / STATUS CHECK
    return jsonResponse({ success: true, message: "Drive Bridge is active and ready." });
  } catch (e) {
    return jsonResponse({ success: false, error: e.toString() });
  }
}

function doPost(e) {
  try {
    let body = {};
    if (e && e.postData && e.postData.contents) {
      body = JSON.parse(e.postData.contents);
    }
    const action = body.action || (e && e.parameter && e.parameter.action);

    // 1. SAVE VOICEOVER.MP3 IN HISTORY SHORTS FOLDER
    if (action === "upload_mp3") {
      const folderId = body.folderId;
      const mp3Base64 = body.mp3Base64;
      const folder = DriveApp.getFolderById(folderId);
      const existing = folder.getFilesByName("voiceover.mp3");
      while (existing.hasNext()) {
        existing.next().setTrashed(true);
      }
      const bytes = Utilities.base64Decode(mp3Base64);
      const blob = Utilities.newBlob(bytes, "audio/mpeg", "voiceover.mp3");
      const file = folder.createFile(blob);
      return jsonResponse({ success: true, fileId: file.getId() });
    }

    // 2. MARK HISTORY SHORT AS UPLOADED
    if (action === "mark_uploaded") {
      const folderId = body.folderId;
      const youtubeUrl = body.youtubeUrl || "";
      const folder = DriveApp.getFolderById(folderId);
      const currentName = folder.getName();
      if (currentName.indexOf("[UPLOADED]") === -1) {
        folder.setName("[UPLOADED] " + currentName);
      }
      if (youtubeUrl) {
        folder.createFile("youtube_url.txt", youtubeUrl);
      }
      return jsonResponse({ success: true, newName: folder.getName() });
    }

    // 3. UPLOAD ANY FILE TO DOCUMENTARY_AUTO FOLDER
    if (action === "upload_file") {
      const fileName = body.name || "uploaded_file";
      const fileBase64 = body.base64;
      const folder = getFolder(DOC_FOLDER_ID);
      const bytes = Utilities.base64Decode(fileBase64);
      const blob = Utilities.newBlob(bytes, "application/octet-stream", fileName);
      const file = folder.createFile(blob);
      return jsonResponse({ success: true, fileId: file.getId() });
    }

    return jsonResponse({ success: false, error: "Unknown action: " + action });
  } catch (e) {
    return jsonResponse({ success: false, error: e.toString() });
  }
}
