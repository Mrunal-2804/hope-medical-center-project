/**
 * Post request handler processing incoming form contents from the Hospital frontend web form.
 * Appends standard appointment requests seamlessly onto an active spreadsheet tracker.
 */
function doPost(e) {
  try {
    // Open targeted tracking spreadsheet via operational active sheet structure
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // Fallback error trap if parsing initialization data objects becomes obstructed
    if (!e || !e.parameter) {
      return ContentService.createTextOutput(JSON.stringify({
        "status": "error", 
        "message": "No parameters detected within the incoming request payload."
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Parse structural elements out of parameters directly matching frontend name properties
    var timestamp = new Date();
    var fullName  = e.parameter.fullName;
    var email     = e.parameter.email;
    var phone     = e.parameter.phone;
    var dept      = e.parameter.department;
    var dateTime  = e.parameter.dateTime;
    var notes     = e.parameter.notes || "None Provided";
    
    // Push the structural details down array tracking system lines cleanly
    sheet.appendRow([
      timestamp, 
      fullName, 
      email, 
      phone, 
      dept, 
      dateTime, 
      notes
    ]);
    
    // Respond back to frontend cleanly using structured JSON string evaluations 
    return ContentService.createTextOutput(JSON.stringify({
      "status": "success",
      "message": "Appointment booked successfully!"
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    // Provide diagnostic telemetry data inside JSON error configurations cleanly
    return ContentService.createTextOutput(JSON.stringify({
      "status": "error",
      "message": error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}