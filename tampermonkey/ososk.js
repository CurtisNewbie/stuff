// ==UserScript==
// @name         ososk.js
// @namespace    http://tampermonkey.net/
// @version      2024-08-05
// @description  try to take over the world!
// @author       You
// @match        https://ososedki.com/photos/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=ososedki.com
// @grant        none
// ==/UserScript==

(function () {
    "use strict";

    let atags = document.querySelectorAll("a");
    let links = [];
    for (let at of atags) {
      if (at.hasAttribute("data-fancybox") && at.hasAttribute("href")) {
        // console.log(at);
        let hr = at.getAttribute("href");
        links.push(hr);
      }
    }

    console.log(links);

    function startDownload() {
      var interval = setInterval(download, 300, links);

      function download(links) {
        var url = links.pop();

        var a = document.createElement("a");
        a.setAttribute("href", url);
        a.setAttribute("download", "");
        a.setAttribute("target", "_blank");
        a.click();

        if (links.length == 0) {
          clearInterval(interval);
        }
      }
    }

    let dbtn = document.createElement("button")
    dbtn.style.margin = "5px";
    dbtn.onclick = startDownload;
    dbtn.textContent = "Download Images";
    document.body.prepend(dbtn);
  })();
