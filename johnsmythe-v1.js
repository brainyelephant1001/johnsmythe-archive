/* John Smythe Research Engine — Version 1.0 — Consolidated client JavaScript */
"use strict";



const form = document.getElementById("researchForm");

const questionInput = document.getElementById("question");

const searchButton = document.getElementById("searchButton");



let currentQuestion = "";

let currentReport = null;
let currentSearchId = null;





const providers = [

  ["UK Government", "gov.uk"],

  ["UK Parliament", "parliament.uk"],

  ["UK Legislation", "legislation.gov.uk"],

  ["Office for National Statistics", "ons.gov.uk"],

  ["National Archives", "nationalarchives.gov.uk"]

];



function element(tag, content = "") {

  const node = document.createElement(tag);

  node.textContent = String(content ?? "");

  return node;

}



function addLink(parent, title, url) {





  if (!url || !/^https?:\/\//i.test(url)) return;



  const link = document.createElement("a");

  link.href = url;

  link.target = "_blank";

  link.rel = "noopener noreferrer";

  link.textContent = title + " ↗";



  parent.appendChild(link);

}



function showSources(question) {

  const container = document.getElementById("sources");

  container.replaceChildren();



  providers.forEach(([name, domain]) => {

    const block = element("div");

    block.className = "source";





    const url = "https://www.google.com/search?q=" +

      encodeURIComponent("site:" + domain + " " + question);





    addLink(block, "Search " + name, url);

    container.appendChild(block);

  });

}





function formatDate(value) {

  if (!value) return "Not supplied";

  const date = new Date(value);

  return Number.isNaN(date.getTime())

    ? value

    : date.toLocaleDateString("en-GB");

}



function renderStatisticsResearch(statisticsResearch) {

  const findings = document.getElementById("findings");



  if (!findings || !statisticsResearch) return;



  const records = Array.isArray(statisticsResearch.records)

    ? statisticsResearch.records : [];



  const section = document.createElement("section");

  section.className = "statistics-research";



  section.appendChild(

    element(

      "h3",

      "Official Statistics — ONS (" + records.length + ")"

    )

  );



  section.appendChild(

    element(

      "p",

      "These are official statistical search results. " +

      "The underlying figures, methodology and any " +

      "relationship to government policy have not yet been assessed."

    )

  );



  if (statisticsResearch.error) {

    section.appendChild(

      element(

        "p",

        "ONS search unavailable: " + statisticsResearch.error

      )

    );

  } else if (!records.length) {

    section.appendChild(

      element("p", "No statistical records returned for this search.")

    );

  }



  for (const record of records) {

    const article = document.createElement("article");



    article.appendChild(

      element("h4", record.title || "Untitled statistic")

    );



    if (record.release_date) {

      article.appendChild(

        element("p", "Released: " + record.release_date)

      );

    }



    if (record.document_type) {

      article.appendChild(

        element("p", "Type: " + record.document_type)

      );

    }



    if (record.description) {

      article.appendChild(

        element("p", record.description)

      );

    }



    if (record.dataset_id) {

      article.appendChild(

        element("p", "Dataset ID: " + record.dataset_id)

      );

    }



    if (record.series_id) {

      article.appendChild(

        element("p", "Series ID: " + record.series_id)

      );

    }



    if (record.url) {

      const link = document.createElement("a");

      link.href = record.url;

      link.target = "_blank";

      link.rel = "noopener noreferrer";

      link.textContent = "View original ONS source";

      article.appendChild(link);

    }



    section.appendChild(article);

  }



  findings.appendChild(section);

}



function renderLegislationResearch(legislationResearch) {

  const findings = document.getElementById("findings");



  if (!findings || !legislationResearch) return;



  const records = Array.isArray(legislationResearch.records)

    ? legislationResearch.records : [];



  const section = document.createElement("section");

  section.className = "legislation-research";



  section.appendChild(

    element("h3", "UK Legislation (" + records.length + ")")

  );



  section.appendChild(

    element(

      "p",

      "Official legislation search results. " +

      "The legal status, amendments and commencement " +

      "of individual provisions have not been assessed."

    )

  );



  if (legislationResearch.error) {

    section.appendChild(

      element(

        "p",

        "Legislation search unavailable: " +

        legislationResearch.error

      )

    );

  } else if (!records.length) {

    section.appendChild(

      element(

        "p",

        "No legislation records returned for this search."

      )

    );

  }



  for (const record of records) {

    const article = document.createElement("article");



    article.appendChild(

      element("h4", record.title || "Untitled legislation")

    );



    if (record.date) {

      article.appendChild(

        element("p", "Published: " + record.date)

      );

    }



    if (record.last_updated) {

      article.appendChild(

        element("p", "Record updated: " + record.last_updated)

      );

    }



    if (record.identifier) {

      article.appendChild(

        element("p", "Identifier: " + record.identifier)

      );

    }



    if (record.url) {

      const link = document.createElement("a");

      link.href = record.url;

      link.target = "_blank";

      link.rel = "noopener noreferrer";

      link.textContent = "View original legislation";

      article.appendChild(link);

    }



    section.appendChild(article);

  }



  findings.appendChild(section);

}



function renderGovernmentResearch(governmentResearch) {

  const findings = document.getElementById("findings");



  if (!findings || !governmentResearch) return;



  const records = Array.isArray(governmentResearch.records)

    ? governmentResearch.records : [];



  const section = document.createElement("section");

  section.className = "government-research";



  section.appendChild(

    element("h3", "GOV.UK Government Publications (" + records.length + ")")

  );



  section.appendChild(

    element(

      "p",

      "These are government search results. " +

      "Their contents and claims have not been independently verified."

    )

  );



  if (governmentResearch.error) {

    section.appendChild(

      element("p", "Government search unavailable: " + governmentResearch.error)

    );

  } else if (!records.length) {

    section.appendChild(

      element("p", "No government publications returned for this search.")

    );

  }



  for (const record of records) {

    const article = document.createElement("article");



    article.appendChild(

      element("h4", record.title || "Untitled publication")

    );



    if (record.date) {

      article.appendChild(

        element("p", "Published: " + record.date)

      );

    }



    if (record.document_type) {

      article.appendChild(

        element("p", "Document type: " + record.document_type)

      );

    }



    if (record.description) {

      article.appendChild(

        element("p", record.description)

      );

    }



    if (record.url) {

      const link = document.createElement("a");

      link.href = record.url;

      link.target = "_blank";

      link.rel = "noopener noreferrer";

      link.textContent = "View original GOV.UK publication";

      article.appendChild(link);

    }



    section.appendChild(article);

  }



  findings.appendChild(section);

}



function renderOfficialSources(sourcePlan) {

  const findings = document.getElementById("findings");



  if (!findings || !sourcePlan) return;



  const sources = Array.isArray(sourcePlan.sources)

    ? sourcePlan.sources : [];



  const section = document.createElement("section");

  section.className = "official-research-sources";



  section.appendChild(

    element("h3", "Explore official research sources")

  );



  section.appendChild(

    element(

      "p",

      "These links help you explore public records. " +

      "They are not retrieved or verified evidence."

    )

  );



  for (const source of sources) {

    const paragraph = document.createElement("p");

    const link = document.createElement("a");



    link.href = source.search_url;

    link.target = "_blank";

    link.rel = "noopener noreferrer";

    link.textContent = source.source_name;



    paragraph.appendChild(link);

    section.appendChild(paragraph);

  }



  findings.prepend(section);

}



function renderRecords(report) {

  const findings = document.getElementById("findings");

  findings.replaceChildren();



  const seenRecords = new Set();
  const records = (Array.isArray(report.evidence) ? report.evidence : [])
    .filter(record => ["UK Parliament", "UK Parliament Hansard"].includes(record.source))
    .filter(record => {
      const key = String(record.source || "") + "|" +
        String(record.record_id || record.reference ||
          [record.title, record.date, record.answer].join("|"));
      if (seenRecords.has(key)) return false;
      seenRecords.add(key);
      return true;
    });



  findings.appendChild(

    element("h3", "Parliamentary records (" + records.length + ")")

  );



  if (!records.length) {

    findings.appendChild(element(

      "p",

      "No parliamentary records retrieved. This can also happen when an official source times out; try again or use the original source links."

    ));

  }



  records.forEach((record, index) => {

    const block = element("article");
    const isHansard = record.source === "UK Parliament Hansard";

    block.className = "record";



    block.appendChild(element(

      "h3",

      (index + 1) + ". " + (record.title || "Parliamentary record")

    ));



    block.appendChild(element(

      "div",

      "Reference: " + (record.reference || "Not supplied")

    ));



    // Evidence relevance indicator

    const relevance = record.relevance_analysis || {};

    const score = Number.isFinite(relevance.score)

      ? relevance.score : null;



    const relevanceText = score === null

      ? "Relevance: Not yet assessed"

      : "Relevance: " + relevance.relevance +

        " (" + score + "% keyword match)";



    const relevanceLabel = element("p", relevanceText);

    relevanceLabel.className = "metadata";

    block.appendChild(relevanceLabel);



    const relevanceNote = element(

      "p",

      "Relevance measures keyword overlap, not whether the evidence is accurate or supports a claim."

    );

    relevanceNote.className = "metadata";

    block.appendChild(relevanceNote);



    const meta = element(

      "p",

      (isHansard ? "Sitting: " : "Tabled: ") + formatDate(record.date) +
      (isHansard ? " | House: " : " | Answered: " + formatDate(record.date_answered) + " | Department: ") +
      (record.department || "Not supplied")

    );

    meta.className = "metadata";

    block.appendChild(meta);



    // Hansard contributions are speeches/statements, not necessarily Q&A.
    const questionText = String(record.question || "").trim();
    const answerText = String(record.answer || "").trim();
    if (isHansard) {
      const contribution = answerText || questionText;
      if (contribution) {
        block.appendChild(element("strong", "Hansard contribution"));
        const details = document.createElement("details");
        details.className = "transcript-details";
        const summary = document.createElement("summary");
        summary.textContent = contribution.slice(0, 230) +
          (contribution.length > 230 ? "…  (Show full contribution)" : "");
        details.appendChild(summary);
        if (contribution.length > 230) {
          const text = element("div", contribution);
          text.className = "answer";
          details.appendChild(text);
        }
        block.appendChild(details);
      } else {
        block.appendChild(element("p", "Contribution text unavailable. See original record."));
      }
    } else {
      block.appendChild(element("strong", "Parliamentary question"));
      block.appendChild(element("p", questionText || "Question text not available."));
      block.appendChild(element("strong", "Parliamentary answer"));
      const answer = element("div", answerText || "Answer text not available.");
      answer.className = "answer";
      if (answerText.length > 1200) {
        const details = document.createElement("details");
        details.className = "transcript-details";
        const summary = element("summary", answerText.slice(0, 230) + "…  (Show full answer)");
        details.appendChild(summary);
        details.appendChild(answer);
        block.appendChild(details);
      } else {
        block.appendChild(answer);
      }
    }
    // Evidence assessment
const assessment = record.evidence_assessment;

if (assessment) {
    const assessmentBox = element("div");
    assessmentBox.className = "answer";

    assessmentBox.appendChild(
        element("strong", "Evidence Assessment")
    );

    assessmentBox.appendChild(
        element(
            "p",
            "Evidence type: " +
            (isHansard ? "Hansard contribution" : (assessment.evidence_type || "Not classified"))
        )
    );

    assessmentBox.appendChild(
        element(
            "p",
            assessment.conclusion ||
            "No assessment available."
        )
    );

    if (Array.isArray(assessment.observations)) {
        assessment.observations.forEach(observation => {
            let statement = String(observation || "");
            // The assessment module uses question/answer terminology even for Hansard.
            // Correct the presentation without changing the underlying source or score.
            if (isHansard) {
                statement = statement
                    .replace(/A parliamentary question is present\. Its wording is not treated as a verified claim\./gi,
                        "A Hansard contribution is present. Its statements have not been independently verified.")
                    .replace(/The source response/gi, "The Hansard contribution");
            }
            if (statement.trim()) {
                assessmentBox.appendChild(element("p", statement));
            }
        });
    }

    assessmentBox.appendChild(
        element(
            "p",
            "Verification status: " +
            (assessment.verified
                ? "Verified"
                : "Not independently verified")
        )
    );

    block.appendChild(assessmentBox);
}



    if (record.url) {

      const source = element("p");

      addLink(source, "View original parliamentary record", record.url);

      block.appendChild(source);

    }



    findings.appendChild(block);

  });



  const limitations = Array.isArray(report.limitations)

    ? report.limitations : [];



  if (limitations.length) {

    findings.appendChild(element("h3", "Research limitations"));

    const list = element("ul");

    limitations.forEach(item => {

      list.appendChild(element("li", item));

    });

    findings.appendChild(list);

  }

}




const progressPanel = document.getElementById("researchProgress");
const progressFill = document.getElementById("progressFill");
const progressPercent = document.getElementById("progressPercent");
const progressTrack = document.getElementById("progressTrack");
const progressRemaining = document.getElementById("progressRemaining");
const progressStage = document.getElementById("progressStage");
const progressTitle = document.getElementById("progressTitle");
let progressTimer = null;
let progressStarted = 0;
const ESTIMATED_SECONDS = 35;

function updateProgress() {
  const elapsed = (Date.now() - progressStarted) / 1000;

  // Estimated progress only.
  const percentage = Math.min(
    95,
    Math.round(95 * (1 - Math.exp(-elapsed / 18)))
  );

  progressFill.style.width = percentage + "%";
  progressPercent.textContent = percentage + "% estimated";
  progressTrack.setAttribute("aria-valuenow", String(percentage));

  const remaining = Math.max(0, Math.ceil(ESTIMATED_SECONDS - elapsed));
  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;

  progressRemaining.textContent = remaining > 0
    ? "Estimated time remaining: " + minutes + "m " + seconds + "s"
    : "Taking longer than estimated — still searching";

  progressStage.textContent = elapsed < 12
    ? "Searching parliamentary records…"
    : elapsed < 28
    ? "Gathering government publications and other sources…"
    : "Waiting for official-source responses…";
}

function startProgress() {
  if (progressTimer !== null) clearInterval(progressTimer);

  progressStarted = Date.now();
  progressPanel.classList.remove("hidden");
  progressTitle.textContent = "Research in progress…";

  updateProgress();
  progressTimer = setInterval(updateProgress, 500);
}

function finishProgress(success) {
  if (progressTimer !== null) clearInterval(progressTimer);
  progressTimer = null;
  if (success) {
    progressFill.style.width = "100%";
    progressPercent.textContent = "Complete";
    progressTrack.setAttribute("aria-valuenow", "100");
    progressTitle.textContent = "Research completed";
    progressStage.textContent = "Results are displayed below.";
    progressRemaining.textContent = "";
  } else {
    progressPanel.classList.add("hidden");
  }
}

function showResearchGuidance(guidance) {
  const panel = document.getElementById("researchGuidance");
  panel.replaceChildren();
  if (!guidance) return;
  const heading = document.createElement("h3");
  heading.textContent = guidance.heading;
  panel.appendChild(heading);
  const notice = document.createElement("p");
  notice.textContent = guidance.notice;
  panel.appendChild(notice);
  const list = document.createElement("ul");
  for (const item of guidance.topics || []) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = item.name;
    li.appendChild(link);
    li.appendChild(document.createTextNode(" — " + item.why));
    list.appendChild(li);
  }
  panel.appendChild(list);
  const next = document.createElement("p");
  next.textContent = guidance.next_steps;
  panel.appendChild(next);
}

form.addEventListener("submit", async event => {

  event.preventDefault();



  currentQuestion = questionInput.value.trim();

  if (!currentQuestion) return;



  currentReport = null;
  currentSearchId = null;
  document.getElementById("testerFeedback").classList.add("hidden");
  document.getElementById("feedbackStatus").textContent = "";
  document.getElementById("feedbackForm").reset();
  document.getElementById("feedbackSubmit").disabled = false;
  document.getElementById("feedbackForm").querySelectorAll("select,textarea").forEach(el => el.disabled = false);

  searchButton.disabled = true;
  searchButton.textContent = "Researching…";
  startProgress();



  document.getElementById("reportTitle").textContent = currentQuestion;

  document.getElementById("brief").classList.remove("hidden");

  document.getElementById("status").textContent = "Searching official sources...";

  document.getElementById("intro").textContent =

    "Searching Parliament, GOV.UK, legislation and ONS in parallel...";



  document.getElementById("findings").replaceChildren();
  showResearchGuidance(null);

  showSources(currentQuestion);



  try {

    const response = await fetch("/api/research", {

      method: "POST",

      headers: {"Content-Type":"application/json"},

      body: JSON.stringify({question:currentQuestion})

    });



    if (!response.ok) {

      throw new Error("Server returned " + response.status);

    }



    currentReport = await response.json();
    currentSearchId = currentReport.search_id || null;
    if (currentSearchId) document.getElementById("testerFeedback").classList.remove("hidden");





    showResearchGuidance(currentReport.research_guidance);
    renderRecords(currentReport.report || {});

    renderGovernmentResearch(currentReport.government_research || {});

    renderLegislationResearch(currentReport.legislation_research || {});

    renderStatisticsResearch(currentReport.statistics_research || {});

    renderOfficialSources(currentReport.source_plan || {});

    displayResearchTimeline(currentReport.report || {});
    finishProgress(true);





    document.getElementById("status").textContent =

      "Source discovery — not independently verified";



    document.getElementById("intro").textContent =

      "Research retrieved on " +

      new Date().toLocaleDateString("en-GB") +

      ". Review original records before drawing conclusions.";



  } catch (error) {
    finishProgress(false);

    document.getElementById("status").textContent =

      "Research request failed";

    document.getElementById("intro").textContent =

      "Unable to retrieve records: " + error.message;

  } finally {

    searchButton.disabled = false;
    searchButton.textContent = "Start research";

  }

});



async function downloadReport(format) {
  if (!currentReport) {
    document.getElementById("exportStatus").textContent = "Run a search before downloading a report.";
    return;
  }
  const status = document.getElementById("exportStatus");
  status.textContent = "Preparing " + format.toUpperCase() + " download...";
  try {
    const response = await fetch("/api/export/" + format, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(currentReport)
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || "Export failed (" + response.status + ")");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "john-smythe-research-brief." + format;
    document.body.appendChild(link);
    link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
    status.textContent = "Your " + format.toUpperCase() + " report is ready.";
  } catch (error) { status.textContent = error.message; }
}
for (const [id, format] of [["downloadWord","docx"],["downloadPdf","pdf"],["downloadJson","json"]]) {
  document.getElementById(id).addEventListener("click", () => downloadReport(format));
}


/*
JOHN SMYTHE RESEARCH ENGINE
Timeline Display — Version 0.1

Displays chronological parliamentary records.
Uses timeline data supplied by server.py.
*/

"use strict";

function displayResearchTimeline(report) {

    const events = Array.isArray(report.timeline)
        ? report.timeline
        : [];

    const findings = document.getElementById("findings");

    if (!findings) {
        return;
    }

    const section = document.createElement("section");
    section.className = "research-timeline";

    const heading = document.createElement("h3");
    heading.textContent = "Research Timeline";
    section.appendChild(heading);

    const description = document.createElement("p");
    description.textContent =
        "Chronological records retrieved from official research sources " +
        "for this research question. " +
        "These records have not been independently verified.";

    section.appendChild(description);

    if (events.length === 0) {

        const empty = document.createElement("p");
        empty.textContent =
            "No dated records are available for this timeline.";

        section.appendChild(empty);
        findings.appendChild(section);
        return;
    }

    let previousYear = null;

    events.forEach((event) => {

        const year = event.year || "Unknown year";

        if (year !== previousYear) {

            const yearHeading = document.createElement("h4");
            yearHeading.textContent = String(year);

            section.appendChild(yearHeading);
            previousYear = year;
        }

        const entry = document.createElement("article");
        entry.className = "timeline-entry";

        const date = document.createElement("strong");
        date.textContent = event.date || "Date unavailable";
        entry.appendChild(date);

        const title = document.createElement("p");
        title.textContent =
            event.title || "Untitled parliamentary record";

        entry.appendChild(title);

        if (event.reference) {

            const reference = document.createElement("small");
            reference.textContent =
                "Parliamentary reference: " + event.reference;

            entry.appendChild(reference);
        }

        if (event.url && /^https:\/\//i.test(event.url)) {

            const linkParagraph = document.createElement("p");
            const link = document.createElement("a");

            link.href = event.url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = "View original record ↗";

            linkParagraph.appendChild(link);
            entry.appendChild(linkParagraph);
        }

        section.appendChild(entry);
    });

    findings.appendChild(section);
}


// Optional feedback is linked to an anonymous search ID.
document.getElementById("feedbackForm").addEventListener("submit", async event => {
  event.preventDefault();
  const status = document.getElementById("feedbackStatus");
  const button = document.getElementById("feedbackSubmit");
  if (!currentSearchId) { status.textContent = "Please run a search first."; return; }
  button.disabled = true;
  status.textContent = "Sending feedback…";
  try {
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        search_id: currentSearchId,
        rating: document.getElementById("feedbackRating").value,
        comment: document.getElementById("feedbackComment").value.trim()
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Feedback service unavailable");
    status.textContent = "Thank you — your feedback was saved.";
    document.getElementById("feedbackForm").querySelectorAll("select,textarea").forEach(el => el.disabled = true);
  } catch (error) {
    status.textContent = error.message + " (No feedback was saved.)";
    button.disabled = false;
  }
});
