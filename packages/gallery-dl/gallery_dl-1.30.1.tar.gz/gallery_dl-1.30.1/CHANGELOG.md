## 1.30.1 - 2025-07-26
### Extractors
#### Additions
- [civitai] add `generated` extractor ([#7796](https://github.com/mikf/gallery-dl/issues/7796))
- [facebook] add `avatar` extractor ([#7848](https://github.com/mikf/gallery-dl/issues/7848))
- [imgadult] add `image` extractor ([#7893](https://github.com/mikf/gallery-dl/issues/7893))
- [itaku] add `following` & `followers` extractors ([#7707](https://github.com/mikf/gallery-dl/issues/7707))
- [leakgallery] add support ([#7872](https://github.com/mikf/gallery-dl/issues/7872))
- [madokami] add `manga` extractor ([#7828](https://github.com/mikf/gallery-dl/issues/7828))
#### Changes
- [civitai] change default `user` includes to `["user-images", "user-videos"]` ([#7874](https://github.com/mikf/gallery-dl/issues/7874))
#### Fixes
- [behance] fix `403 Forbidden` errors by using `"browser": "firefox"` ([#7803](https://github.com/mikf/gallery-dl/issues/7803) [#7877](https://github.com/mikf/gallery-dl/issues/7877))
- [civitai] fix `AttributeError` when a file's post was deleted ([#7860](https://github.com/mikf/gallery-dl/issues/7860))
- [pornhub] fix `gallery` extractor ([#7842](https://github.com/mikf/gallery-dl/issues/7842))
- [readcomiconline] force `One page` reading mode ([#7890](https://github.com/mikf/gallery-dl/issues/7890))
- [sexcom] update `search` extractor ([#7807](https://github.com/mikf/gallery-dl/issues/7807))
- [urlgalleries] fix extraction ([#7858](https://github.com/mikf/gallery-dl/issues/7858))
- [wikimedia] add missing `self` argument when calling `prepare()` ([#7835](https://github.com/mikf/gallery-dl/issues/7835))
#### Improvements
- [4chan] detect files containing only null bytes ([#7883](https://github.com/mikf/gallery-dl/issues/7883))
- [azurelanewiki] prevent Anubis challenge
- [bilibili] warn about blocked articles ([#7880](https://github.com/mikf/gallery-dl/issues/7880))
- [civitai] fix `extension` for videos without `name` and `mimeType`
- [common] detect Cloudflare & DDoS-Guard challenge pages in `request_json()` & `request_xml()` ([#7833](https://github.com/mikf/gallery-dl/issues/7833))
- [facebook] add retries to profile page requests ([#7725](https://github.com/mikf/gallery-dl/issues/7725) [#7834](https://github.com/mikf/gallery-dl/issues/7834) [#7852](https://github.com/mikf/gallery-dl/issues/7852))
- [facebook] implement `include` option ([#7848](https://github.com/mikf/gallery-dl/issues/7848))
- [itaku] implement `include` option ([#7707](https://github.com/mikf/gallery-dl/issues/7707))
- [patreon] implement `cursor` support ([#7856](https://github.com/mikf/gallery-dl/issues/7856))
- [patreon] support `date-max` for `/home` URLs ([#7856](https://github.com/mikf/gallery-dl/issues/7856))
- [pixiv] improve AJAX error messages ([#7896](https://github.com/mikf/gallery-dl/issues/7896))
#### Metadata
- [behance] provide `creator[name]` metadata ([#7885](https://github.com/mikf/gallery-dl/issues/7885))
- [civitai] ensure `file` & `post` data has a `date` value ([#7548](https://github.com/mikf/gallery-dl/issues/7548))
- [inkbunny] enable `pool` metadata ([#7850](https://github.com/mikf/gallery-dl/issues/7850))
- [nhentai] provide `gallery_id` for pagination results ([#7868](https://github.com/mikf/gallery-dl/issues/7868))
### Downloaders
- [ytdl] add `deprecations` option
### Post Processors
- [exec] add `session` option ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
### Snap
- migrate base to `core22` ([#7841](https://github.com/mikf/gallery-dl/issues/7841))
- switch to `yt-dlp` ([#7865](https://github.com/mikf/gallery-dl/issues/7865))
- fix deprecated `CRAFT_ARCH_TRIPLET` usage ([#7866](https://github.com/mikf/gallery-dl/issues/7866))
### Formatter
- add `Jinja` template support ([#1390](https://github.com/mikf/gallery-dl/issues/1390))
- add `W` conversion - sanitize whitespace ([#6582](https://github.com/mikf/gallery-dl/issues/6582))
### Miscellaneous
- [actions] fix `parse_logging` import ([#7837](https://github.com/mikf/gallery-dl/issues/7837))
- [options] add `--sleep-429` command-line option ([#7871](https://github.com/mikf/gallery-dl/issues/7871))
- [scripts] ensure files use `utf-8` encoding and `\n` newlines ([#7872](https://github.com/mikf/gallery-dl/issues/7872))
- [tests/extractor] improve example URL mismatch error message ([#7872](https://github.com/mikf/gallery-dl/issues/7872))
- [tests/results] fix `#log` checks for URLs raising exceptions
- fix exit status for requests' `JSONDecodeError` ([#4380](https://github.com/mikf/gallery-dl/issues/4380))
- use walrus operators `:=` in `if` statements ([#7671](https://github.com/mikf/gallery-dl/issues/7671))
