if(!self.define){let e,s={};const i=(i,c)=>(i=new URL(i+".js",c).href,s[i]||new Promise((s=>{if("document"in self){const e=document.createElement("script");e.src=i,e.onload=s,document.head.appendChild(e)}else e=i,importScripts(i),s()})).then((()=>{let e=s[i];if(!e)throw new Error(`Module ${i} didn’t register its module`);return e})));self.define=(c,r)=>{const n=e||("document"in self?document.currentScript.src:"")||location.href;if(s[n])return;let d={};const o=e=>i(e,n),a={module:{uri:n},exports:d,require:o};s[n]=Promise.all(c.map((e=>a[e]||o(e)))).then((e=>(r(...e),d)))}}define(["./workbox-05e2840a"],(function(e){"use strict";self.addEventListener("message",(e=>{e.data&&"SKIP_WAITING"===e.data.type&&self.skipWaiting()})),e.precacheAndRoute([{url:"css/dark-light.css",revision:"8b8dd009d7ce797ef8eb3121bc932f9f"},{url:"css/markdown.css",revision:"dfafafb4bb300d0f61dd796fabcca301"},{url:"css/styles.css",revision:"0d6d8383ac59f1e8c75ea174fb7c7456"},{url:"css/tailwind.min.css",revision:"e35af4d8ceb624072098fa9a3d970aaa"},{url:"favicon.ico",revision:"fdef36b3016bf5ed43c78a64452f9165"},{url:"icons/icon-192x192.png",revision:"1871e64701bdceafc65ae57de7897679"},{url:"icons/icon-512x512.png",revision:"d00a2f911d324f5aa72bc7653a0974e5"},{url:"index.html",revision:"c492706684dc4f1b0a8b6a46bbb08464"},{url:"manifest.json",revision:"6d891bb2a27671e417c3a445b5d4d8c1"},{url:"scripts/feedback.js",revision:"e31e92ef5cd9276cb1e9d15220434997"},{url:"scripts/language.js",revision:"45f80cfd57ac798ceeee2ec9d721ae86"},{url:"scripts/script.js",revision:"b8b54c2966772acdc90adb08e7fdd59d"},{url:"scripts/theme.js",revision:"54ad88ed7d568b67b47f9925b77141a6"},{url:"translations.json",revision:"deb0f3789bb6b0ee549bc9297e3a976d"}],{ignoreURLParametersMatching:[/^utm_/,/^fbclid$/]})}));
//# sourceMappingURL=service-worker.js.map
