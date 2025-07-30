// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import React from "react";
import { Segment } from "semantic-ui-react";

export const CatalogueTreeItem = ({ nodeData = {}, nodeToggle }) => {
  return (
    <g>
      <text style={{ font: "italic 20px serif", fill: "black" }} onClick={nodeToggle}>
        {nodeData.name}
      </text>
    </g>
  );
};

export const renderCustomNode = ({ nodeDatum, toggleNode }) => (
  <CatalogueTreeItem nodeData={nodeDatum} triggerNodeToggle={toggleNode} />
);
