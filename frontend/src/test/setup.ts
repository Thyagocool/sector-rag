import '@testing-library/jest-dom'

// jsdom nao implementa scrollTo
Element.prototype.scrollTo = () => {};

