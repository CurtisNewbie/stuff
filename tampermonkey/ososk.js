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
            let hr = at.getAttribute("href");
            links.push(hr);
            console.log(`Found image link: ${hr}`);
        }
    }

    let newBtn = (txt, fun) => {
        let btn = document.createElement("button");
        btn.style.margin = "5px";
        btn.onclick = fun;
        btn.textContent = txt;
        return btn;
    }

    let downInterval = None;
    let stopDownload = () => {
        if (downInterval) {
            clearInterval(downInterval);
        }
    }

    let startDownload = () => {
        if (downInterval) {
            clearInterval(downInterval);
        }
        downInterval = setInterval((links) => {
            let href = links.pop();
            let a = document.createElement("a");
            a.setAttribute("href", href);
            a.setAttribute("download", "");
            a.setAttribute("target", "_blank");
            a.click();
            console.log(`Clicked ${href}`)

            if (links.length == 0) {
                console.log("download completed")
                clearInterval(downInterval);
            }
        }, 500, links);
    }

    document.body.prepend(newBtn("Stop Download", stopDownload));
    document.body.prepend(newBtn("Download All Images", startDownload));
})();
