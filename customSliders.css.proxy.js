// [snowpack] add styles to the page (skip if no document exists)
if (typeof document !== 'undefined') {
  const code = "\n\n\n.noUi-tooltip {\n  color:white;\n  background:#b30000;\n  display: none ;\n  border: none;\n}\n\n.noUi-active .noUi-tooltip {\n  display: block;\n}\n\n.noUi-state-drag .noUi-tooltip {\n  display: block;\n}\n\n.noUi-marker-horizontal.noUi-marker-sub{\n  height:5px;\n}\n\n.noUi-marker-horizontal.noUi-marker-large{\n  height:8px;\n}\n\n  /* #fdbb84;  */\n  /* #fc8d59;  */\n  /* #e34a33;  */\n  /* #b30000;  */\n\n.noUi-handle {\n  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;\n  border: none;\n  \n  background:#e34a33;\n  width: 16px !important;\n  right: -8px !important;\n  border-radius: 5px; \n}\n\n.noUi-active.noUi-handle {\n  border:1px solid #410000;\n}\n\n.noUi-state-drag .noUi-handle {\n  background:#b30000;\n}\n\n.noUi-handle:after,\n.noUi-handle:before {\n  content: none;\n  font-size: 10px;\n}\n\n.noUi-connect{\n  background:#e34a33;\n}\n\n.noUi-state-drag .noUi-connect{\n  background:#b30000;\n}\n\n\n\n.noUi-handle:before {\n  content:none;\n  display:none;\n}\n\n.noUi-handle:after {\n  content:none;\n  display:none;\n}\n\n.noUi-value-sub{\n  color:#999999\n}";

  const styleEl = document.createElement("style");
  const codeEl = document.createTextNode(code);
  styleEl.type = 'text/css';
  styleEl.appendChild(codeEl);
  document.head.appendChild(styleEl);
}