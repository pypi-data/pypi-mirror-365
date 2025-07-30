// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import React, { Component, PureComponent } from "react";
import { Menu, Popup } from "semantic-ui-react";

export class ContextMenu extends PureComponent {
  render() {
    const { visible, x, y, onAction, node } = this.props;

    if (!visible) {
      return null;
    }

    return (
      <Popup
        open
        position="top left"
        style={{
          position: "absolute",
          top: `${x}px`,
          left: `${y}px`,
          zIndex: 1000,
        }}
      >
        <Menu vertical>
          <Menu.Item style={{ cursor: "pointer" }} onClick={() => onAction("add", node)}>
            Add
          </Menu.Item>
          <Menu.Item style={{ cursor: "pointer" }} onClick={() => onAction("remove", node)}>
            Remove
          </Menu.Item>
          <Menu.Item style={{ cursor: "pointer" }} onClick={() => onAction("edit", node)}>
            Edit
          </Menu.Item>
        </Menu>
      </Popup>
    );
  }
}
