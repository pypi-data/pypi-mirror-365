// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import get from "lodash";
import PropTypes from "prop-types";
import React, { Component, createRef } from "react";
import { AccordionField } from "react-invenio-forms";
import { Card, Grid, Ref, Sticky } from "semantic-ui-react";

import { DepositFormApp, FormFeedback } from "@js/invenio_rdm_records";
import { MetadataFields } from "@js/invenio_records_marc21/components";
import { i18next } from "@translations/invenio_catalogue_marc21/i18next";

import { CatalogueTree, ManageRecord, Marc21CatalogueSerializer } from "./components";

export class CatalogueDepositForm extends Component {
  accordionStyle = {
    header: { className: "segment inverted brand" },
  };

  constructor(props) {
    super(props);

    const { files, record } = this.props;

    this.props = props;
    this.config = props.config || {};
    this.templates = props.templates || [];
    this.files = props.files;
    this.recordSerializer = new Marc21CatalogueSerializer();

    this.noFiles = false;
    if (
      !Array.isArray(files.entries) ||
      (!files.entries.length && record.is_published)
    ) {
      this.noFiles = true;
    }
  }

  render() {
    const { record, files, permissions, preselectedCommunity } = this.props;
    const allowRecordRestriction = true;

    return (
      <DepositFormApp
        config={this.config}
        record={record}
        preselectedCommunity={preselectedCommunity}
        files={files}
        permissions={permissions}
        recordSerializer={this.recordSerializer}
      >
        <FormFeedback fieldPath="message" />
        <>
          {this.noFiles && record.is_published && (
            <div className="text-align-center pb-10">
              <em>{i18next.t("The record has no files.")}</em>
            </div>
          )}
          <Grid>
            <Grid.Row>
              <Grid.Column className="left-sidebar" computer={5}>
                <CatalogueTree
                  label={i18next.t("Catalogue")}
                  labelIcon="space shuttle"
                  fieldPath="catalgoue"
                  catalogue={record.tree}
                  onError={() => {}}
                />
              </Grid.Column>

              <Grid.Column className="main-column" computer={8}>
                <MetadataFields className={"metadata"} fieldPath="metadata" />
              </Grid.Column>

              <Grid.Column className="right-sidebar" computer={3}>
                <ManageRecord
                  record={record}
                  permissions={permissions}
                  alloweRecordRestriction={allowRecordRestriction}
                  templates={this.templates}
                  config={this.config}
                />
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </>
      </DepositFormApp>
    );
  }
}
