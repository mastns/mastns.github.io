# mastrogeorgiou.gr

Personal website of Athanasios (Thanasis) Mastrogeorgiou, robotics researcher: https://mastrogeorgiou.gr/

A single static page (`index.html` + `assets/style.css`) served by GitHub Pages from `master`.
`CNAME` makes mastrogeorgiou.gr the site's address; https://mastns.github.io/ redirects there.
`mastrogeorgiou.github.io/` redirects the old project-site address to the root.

## Hosting note (transition)

Until the domain's DNS points at GitHub Pages (apex `A` records 185.199.108.153, .109.153, .110.153, .111.153;
`www` can stay a CNAME to the apex), mastrogeorgiou.gr is still answered by the Papaki/Plesk host, and
`.github/workflows/deploy-mastrogeorgiou-gr.yml` mirrors the site there over FTPS on every push.
At the switch: delete that workflow and the `FTP_USERNAME` / `FTP_PASSWORD` secrets, then enable
"Enforce HTTPS" in the repository's Pages settings once GitHub has issued the certificate.
