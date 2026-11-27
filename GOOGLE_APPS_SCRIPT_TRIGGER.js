/**
 * Google Apps Script - Autonomous YouTube + Facebook + Instagram Cloud Trigger
 * Faraz Sir's Multi-Channel Cloud Autopilot Engine
 *
 * Runs in Google Apps Script (script.google.com) on a daily timer.
 * Sends a webhook to GitHub Actions (flintgrit-cloud-engine), which runs with
 * UNLIMITED FREE CLOUD MINUTES even when PC is completely turned OFF!
 */

const GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN";
const REPO_OWNER = "ashrafnadim47-creator";
const REPO_NAME = "flintgrit-cloud-engine";

function triggerWorkflow(workflowFile, inputs) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${workflowFile}/dispatches`;

  const payload = JSON.stringify({
    ref: "main",
    inputs: inputs || {}
  });

  const options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "Authorization": "Bearer " + GITHUB_TOKEN,
      "Accept": "application/vnd.github+json",
      "User-Agent": "Google-Apps-Script-Autopilot"
    },
    payload: payload,
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  Logger.log(workflowFile + " Trigger Status: " + response.getResponseCode());
}

function triggerViceCityPulse() {
  triggerWorkflow("channel2_vice_city_pulse.yml", { upload_to_youtube: "true" });
}

function triggerHistoryShorts() {
  triggerWorkflow("daily_history_shorts.yml", {});
}

function triggerDocumentary() {
  triggerWorkflow("daily_documentary.yml", {});
}

function triggerShadowWill() {
  triggerWorkflow("channel1_ricksclips_cloud.yml", { upload_to_youtube: "true" });
}
