// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Catalogue-Marc21 is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import axios from "axios";
import React, { PureComponent } from "react";
import { connect } from "react-redux";
import {
  Button,
  Modal,
  ModalActions,
  ModalContent,
  ModalHeader,
} from "semantic-ui-react";

function modalLocalReducer(state, action) {
  switch (action.type) {
    case "close":
      return { ...state, open: false };
    case "open":
      return { ...state, open: true, size: action.size };
    case "search":
      return { ...state, open: false };
    default:
      return state;
  }
}

class ImportFromAlmaCmp extends PureComponent {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      size: undefined,
    };
    this.inputRef = React.createRef();
  }

  dispatch = (action) => {
    this.setState((prevState) => modalLocalReducer(prevState, action));
  };

  handleOpen = () => {
    this.dispatch({ type: "open", size: "mini" });
  };

  handleClose = () => {
    this.dispatch({ type: "close" });
  };

  handleSearch = async () => {
    const value = this.inputRef.current.value;
    const type = value.startsWith("AC") ? "ac_number" : "mmsid";
    let data = {};
    try {
      let apiConfig = {
        withCredentials: true,
        xsrfCookieName: "csrftoken",
        xsrfHeaderName: "X-CSRFToken",
        headers: { Accept: "application/json" },
      };
      let axiosWithConfig = axios.create(apiConfig);
      const url = `/api/catalogue/alma/${type}/${value}`;
      const response = await axiosWithConfig.get(url);
      data = response.data;
      // data = {
      //   metadata: {
      //     fields: [],
      //     leader: "fasr"
      //   },
      //   catalogue: {
      //     root: "",
      //     parent: "",
      //     children: []
      //   }
      // }
    } catch (error) {
      console.log("CreateNode error: ", error);
    }

    const { saveAction } = this.props;

    saveAction(data);

    this.dispatch({ type: "search" });
  };

  render() {
    const { open, size } = this.state;

    return (
      <>
        <Button
          compact
          fluid
          onClick={this.handleOpen}
          icon="search"
          labelPosition="left"
          content="import from alma"
        />
        <Modal size={size} open={open} onClose={this.handleClose}>
          <ModalHeader>Import from Alma</ModalHeader>
          <ModalContent>
            <input ref={this.inputRef} placeholder="Enter mmsid or ac number" />
          </ModalContent>
          <ModalActions>
            <Button negative onClick={this.handleClose}>
              Close
            </Button>
            <Button positive onClick={this.handleSearch}>
              Search
            </Button>
          </ModalActions>
        </Modal>
      </>
    );
  }
}

function save(data) {
  // maybe not necessary that complicated but it does work like that
  // name should be different, because it does not save the record
  // it does only updating the record
  return async (dispatch) => {
    dispatch({
      type: "DRAFT_SAVE_SUCCEEDED",
      payload: { data: data },
    });
  };
}

const mapStateToProps = null;

const mapDispatchToProps = (dispatch) => ({
  saveAction: (values) => dispatch(save(values)),
});

export const ImportFromAlma = connect(
  mapStateToProps,
  mapDispatchToProps
)(ImportFromAlmaCmp);
