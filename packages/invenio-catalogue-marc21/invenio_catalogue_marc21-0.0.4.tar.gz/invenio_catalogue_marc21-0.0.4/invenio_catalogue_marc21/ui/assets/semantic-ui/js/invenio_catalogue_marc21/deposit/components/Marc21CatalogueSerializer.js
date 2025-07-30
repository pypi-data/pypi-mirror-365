// This file is part of Invenio.
//
// Copyright (C) 2021-2025 Graz University of Technology.
//
// React-Records-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import { get, set } from "lodash";

import { Marc21RecordSerializer } from "@js/invenio_records_marc21/components";

export class Marc21CatalogueSerializer extends Marc21RecordSerializer {
  constructor(defaultLocale) {
    super();
    this.defaultLocale = defaultLocale;
    this.current_record = {};
  }

  /**
   * Deserialize backend record into format compatible with frontend.
   * @method
   * @param {object} record - potentially empty object
   * @returns {object} frontend compatible record object
   */
  deserialize(record) {
    this.current_record = record;
    return record;
  }

  /**
   * Deserialize backend record errors into format compatible with frontend.
   * @method
   * @param {array} errors - array of error objects
   * @returns {object} - object representing errors
   */
  deserializeErrors(errors) {
    return super.deserializeErrors(errors);
  }

  /**
   * Serialize record to send to the backend.
   * @method
   * @param {object} record - in frontend format
   * @returns {object} record - in API format
   *
   */
  serialize(record) {
    return record;
  }
}
