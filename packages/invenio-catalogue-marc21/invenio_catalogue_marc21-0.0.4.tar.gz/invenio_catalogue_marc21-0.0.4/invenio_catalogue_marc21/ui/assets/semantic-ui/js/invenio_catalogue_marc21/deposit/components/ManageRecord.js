// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import React, { Component } from "react";
import { Card, Divider, Grid } from "semantic-ui-react";

import {
  AccessRightField,
  DeleteButton,
  FileUploader,
  SaveButton,
} from "@js/invenio_rdm_records";
import {
  AccessMessage,
  EmbargoAccess,
  FilesAccess,
  MetadataAccess,
} from "@js/invenio_rdm_records/src/deposit/fields/AccessField/components";
import { TemplateField } from "@js/invenio_records_marc21/components";
import { i18next } from "@translations/invenio_catalogue_marc21/i18next";

import { ImportFromAlma } from "./ImportFromAlma";

export class ManageRecord extends Component {
  state = {};

  constructor(props) {
    super(props);
  }

  render() {
    const { record, permissions, allowRecordRestriction, templates, config } =
      this.props;
    return (
      <Card>
        <Card.Content>
          <Grid relaxed>
            <Grid.Column width={16}>
              <SaveButton fluid />

              {permissions?.can_delete_draft && (
                <DeleteButton
                  fluid
                  // TODO: make is_published part of the API response
                  //       so we don't have to do this
                  isPublished={record.is_published}
                />
              )}

              {templates.length > 0 && (
                <TemplateField
                  label={i18next.t("Templates")}
                  labelIcon={"bookmark"}
                  templates={templates}
                />
              )}

              {permissions?.showMetadataAccess && (
                <>
                  <MetadataAccess record={record} />
                  <Divider hidden />
                </>
              )}

              {permissions?.showFileAccess && (
                <>
                  <FilesAccess />
                  <Divider hidden />
                </>
              )}

              {permissions?.showImportFromAlma && <ImportFromAlma />}

              {permissions?.showFileUploader && (
                <FileUploader
                  isDraftRecord={!record.is_published}
                  quota={config.quota}
                  decimalSizeDisplay={config.decimal_size_display}
                />
              )}


            </Grid.Column>
          </Grid>
        </Card.Content>
      </Card>
    );
  }
}
