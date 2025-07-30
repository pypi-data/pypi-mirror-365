// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import axios from "axios";
import { connect as connectFormik } from "formik";
import PropTypes from "prop-types";
import React, { useState } from "react";
// import Tree from "react-d3-tree";
import { FieldLabel } from "react-invenio-forms";
import { connect } from "react-redux";
import { Card, Form, Header, Loader } from "semantic-ui-react";

// TODO: import i18next from invenio_catalogue_marc21
import { i18next } from "@translations/invenio_records_marc21/i18next";

import { renderCustomNode } from "./CatalogueTreeItem";
import { Tree } from "./Tree";

export const CatalogueTree = ({
  label,
  labelIcon,
  fieldPath,
  onError,
  catalogue,
  actionState,
}) => {
  return (
    <Card className="catalogue-field" fluid>
      <Card.Content>
        <Tree data={catalogue} />
      </Card.Content>
    </Card>
  );
};
