// This file is part of Invenio.
//
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import $ from "jquery";
import React from "react";
import ReactDOM from "react-dom";
import { getInputFromDOM } from "@js/invenio_rdm_records";
import { CatalogueDepositForm } from "@js/invenio_catalogue_marc21/deposit/CatalogueDepositForm";
// import { RecordManagement } from "@js/invenio_records_marc21/Marc21RecordManagement";
// import { RecordVersionsList } from "@js/invenio_records_marc21/Marc21RecordVersionsList";
// import { ExportDropdown } from "@js/invenio_app_rdm/landing_page/ExportDropdown";

const depositContainerDiv = document.getElementById("marc21-catalogue-deposit-page");
const depositLeftContainerDiv = document.getElementById("marc21-catalogue-deposit-left-container");
const depositMiddleContainerDiv = document.getElementById("marc21-catalogue-deposit-middle-container");
const depositRightContainerDiv = document.getElementById("marc21-catalogue-deposit-right-container");

if (depositContainerDiv) {
  ReactDOM.render(
    <CatalogueDepositForm
      record={getInputFromDOM("marc21-catalogue-deposit-record")}
      files={getInputFromDOM("marc21-catalogue-deposit-files")}
      config={getInputFromDOM("marc21-catalogue-deposit-config")}
      templates={getInputFromDOM("marc21-catalogue-deposit-templates")}
      permissions={getInputFromDOM("marc21-catalogue-deposit-permissions")}
    />,
    depositContainerDiv
  );
}

// if (recordVersionsAppDiv) {
//   ReactDOM.render(
//     <RecordVersionsList
//       record={JSON.parse(recordVersionsAppDiv.dataset.record)}
//       isPreview={JSON.parse(recordVersionsAppDiv.dataset.preview)}
//     />,
//     recordVersionsAppDiv
//   );
// }

// if (recordExportDownloadDiv) {
//   ReactDOM.render(
//     <ExportDropdown
//       formats={JSON.parse(recordExportDownloadDiv.dataset.formats)}
//     />,
//     recordExportDownloadDiv
//   );
// }

// $(".ui.accordion").accordion({
//   selector: {
//     trigger: ".title .dropdown",
//   },
// });

// $(".ui.tooltip-popup").popup();

// $(".preview-link").on("click", function (event) {
//   $("#preview").find(".title").html(event.target.dataset.fileKey);
// });

// $("#jump-btn").on("click", function (event) {
//   document.documentElement.scrollTop = 0;
// });

// // func to toggle the icon class
// $(".panel-heading").click(function () {
//   $("i", this).toggleClass("down right");
// });

// $("#record-doi-badge").on("click", function () {
//   $("#doi-modal").modal("show");
// });
