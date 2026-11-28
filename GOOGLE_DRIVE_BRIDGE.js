/**
 * =============================================================================
 * GOOGLE APPS SCRIPT - MASTER DRIVE BRIDGE FOR DOCUMENTARY & HISTORY SHORTS
 * Faraz Sir's Multi-Channel Cloud Engine (Chronicle Vault)
 * =============================================================================
 * 
 * Instructions:
 * 1. Open https://script.google.com
 * 2. Paste this entire code into your Apps Script project.
 * 3. Click 'Deploy' -> 'New deployment' (or 'Manage deployments' -> Edit).
 * 4. Select type: 'Web app'
 *    - Execute as: 'Me' (your google account)
 *    - Who has access: 'Anyone'
 * 5. Click Deploy and copy the Web App URL (ends in /exec).
 * 6. Save this URL into GitHub Secrets as 'DRIVE_BRIDGE_URL'.
 * =============================================================================
 */

const DOC_FOLDER_ID = "1KfsTib0zr1vRYJc_xEXjNod8hyReCa0e"; // Documentary_Auto folder
const HISTORY_FOLDER_NAME = "HistoryShorts_Auto";

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
    const action = (e.parameter && e.parameter.action) || "list";

    // 1. LIST FILES IN DOCUMENTARY_AUTO FOLDER
    if (action === "list") {
      const folder = getFolder(DOC_FOLDER_ID);
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

    // 2. DOWNLOAD FILE AS BASE64 BY NAME
    if (action === "get_base64") {
      const name = e.parameter.name;
      const folder = getFolder(DOC_FOLDER_ID);
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
          let meta = {};
          const metaFiles = sub.getFilesByName("metadata.json");
          if (metaFiles.hasNext()) {
            try {
              meta = JSON.parse(metaFiles.next().getBlob().getDataAsString("UTF-8"));
            } catch (err) {}
          }
          return jsonResponse({
            found: true,
            folderId: sub.getId(),
            folderName: sub.getName(),
            mp4Base64: Utilities.base64Encode(mf.getBlob().getBytes()),
            meta: meta
          });
        }
      }
      return jsonResponse({ found: false });
    }

    return jsonResponse({ status: "alive", message: "Drive Bridge is active." });
  } catch (err) {
    return jsonResponse({ error: err.toString() });
  }
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;

    // 1. UPLOAD VOICEOVER.MP3 TO SUBFOLDER
    if (action === "upload_mp3") {
      const folder = DriveApp.getFolderById(data.folderId);
      const old = folder.getFilesByName("voiceover.mp3");
      while (old.hasNext()) { old.next().setTrashed(true); }
      const bytes = Utilities.base64Decode(data.mp3Base64);
      const blob = Utilities.newBlob(bytes, "audio/mpeg", "voiceover.mp3");
      const f = folder.createFile(blob);
      return jsonResponse({ success: true, fileId: f.getId() });
    }

    // 2. MARK SUBFOLDER AS UPLOADED
    if (action === "mark_uploaded") {
      const folder = DriveApp.getFolderById(data.folderId);
      folder.setName("[UPLOADED] " + folder.getName());
      if (data.youtubeUrl) {
        folder.createFile("youtube_link.txt", data.youtubeUrl);
      }
      return jsonResponse({ success: true });
    }

    // 3. SAVE GENERAL DOCUMENTARY FILE TO DOC_FOLDER_ID
    if (data.name && data.base64) {
      const folder = getFolder(DOC_FOLDER_ID);
      const old = folder.getFilesByName(data.name);
      while (old.hasNext()) { old.next().setTrashed(true); }
      const bytes = Utilities.base64Decode(data.base64);
      const blob = Utilities.newBlob(bytes, data.mimeType || "application/octet-stream", data.name);
      const f = folder.createFile(blob);
      return jsonResponse({ success: true, fileId: f.getId() });
    }

    return jsonResponse({ success: false, error: "Unknown POST action" });
  } catch (err) {
    return jsonResponse({ success: false, error: err.toString() });
  }
}
