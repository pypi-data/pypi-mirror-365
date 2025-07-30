/**
 * ESLint 9.x configuration for React JavaScript project
 * Converted from legacy .eslintrc format with modern alternatives
 */

import js from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y";
import prettier from "eslint-plugin-prettier";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";

export default [
  // Base JavaScript recommended rules
  js.configs.recommended,

  // Main configuration
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.es2021,
        ...globals.jest,
        ...globals.node,
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
      "jsx-a11y": jsxA11y,
      prettier,
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    rules: {
      // Prettier integration
      "prettier/prettier": "error",

      // General JavaScript rules
      "camelcase": [
        "error",
        {
          properties: "never",
          ignoreDestructuring: true,
        },
      ],

      // React rules
      "react/react-in-jsx-scope": "off", // Not needed in React 17+
      "react/jsx-uses-react": "off", // Not needed in React 17+
      "react/prop-types": "warn", // Made less strict as modern alternative
      "react/button-has-type": "warn",
      "react/default-props-match-prop-types": "error",
      "react/destructuring-assignment": "warn",
      "react/display-name": "error",
      "react/no-access-state-in-setstate": "warn",
      "react/no-array-index-key": "warn",
      "react/jsx-boolean-value": "error",
      "react/jsx-closing-bracket-location": ["error", "tag-aligned"],
      "react/jsx-closing-tag-location": "error",
      "react/jsx-curly-brace-presence": [
        "error",
        {
          props: "never",
        },
      ],
      "react/jsx-curly-spacing": "error",
      "react/jsx-equals-spacing": "error",
      "react/jsx-filename-extension": [
        "warn",
        {
          extensions: [".jsx", ".js"],
        },
      ],
      "react/jsx-indent-props": ["error", "first"],
      "react/jsx-key": "error",
      "react/jsx-no-comment-textnodes": "error",
      "react/jsx-no-duplicate-props": "error",
      "react/jsx-no-undef": "error",
      "react/jsx-no-useless-fragment": "warn",
      "react/jsx-pascal-case": "error",
      "react/jsx-props-no-multi-spaces": "error",
      "react/jsx-tag-spacing": [
        "error",
        {
          closingSlash: "never",
          beforeSelfClosing: "always",
          afterOpening: "never",
          beforeClosing: "never",
        },
      ],
      "react/jsx-uses-vars": "error",
      "react/jsx-wrap-multilines": [
        "error",
        {
          declaration: "parens-new-line",
          assignment: "parens-new-line",
          return: "parens-new-line",
          arrow: "parens-new-line",
          condition: "parens-new-line",
          logical: "parens-new-line",
          prop: "ignore",
        },
      ],
      "react/no-children-prop": "error",
      "react/no-danger-with-children": "error",
      "react/no-deprecated": "error",
      "react/no-did-mount-set-state": "error",
      "react/no-did-update-set-state": "error",
      "react/no-direct-mutation-state": "error",
      "react/no-find-dom-node": "error",
      "react/no-is-mounted": "error",
      "react/no-multi-comp": "off",
      "react/no-redundant-should-component-update": "error",
      "react/no-render-return-value": "error",
      "react/no-string-refs": "error",
      "react/no-this-in-sfc": "error",
      "react/no-typos": "error",
      "react/no-unescaped-entities": [
        "error",
        {
          forbid: [">", "}"],
        },
      ],
      "react/no-unknown-property": "error",
      "react/no-unused-prop-types": "error",
      "react/no-unused-state": "error",
      "react/no-will-update-set-state": "error",
      "react/prefer-es6-class": "error",
      "react/require-default-props": "warn",
      "react/require-render-return": "error",
      "react/self-closing-comp": "error",
      "react/sort-comp": "warn",
      "react/void-dom-elements-no-children": "error",

      // React Hooks rules (modern addition)
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      // JSX Accessibility rules
      ...jsxA11y.configs.recommended.rules,
    },
  },

  // Ignore patterns (replaces .eslintignore)
  {
    ignores: [
      "dist/**",
      "build/**",
      "node_modules/**",
      "coverage/**",
      "*.config.js",
      "*.config.mjs",
    ],
  },
];
