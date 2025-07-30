const config = {
  plugins: ["@ianvs/prettier-plugin-sort-imports"],
  printWidth: 88, // as in Black for Python
  tabWidth: 2,
  useTabs: false,
  semi: true,
  singleQuote: false, // as in Black for Python
  quoteProps: "consistent",
  jsxSingleQuote: false,
  trailingComma: "es5",
  bracketSpacing: true,
  arrowParens: "always",
  endOfLine: "lf",
  importOrder: [
    "",
    "<THIRD_PARTY_MODULES>", // Imports not matched by other special words or groups.
    "",
    "<BUILTIN_MODULES>", // Node.js built-in modules
    "",
    "^(@js|@translations)/(.*)$",
    "^/(.*)$",
    "",
    "^[.]", // relative imports
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
};

export default config;
