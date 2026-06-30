# Inceptor blog generator

Tool to generate static blog websites, that have lightspeed loadtime.

# Usage
```sh
# generates dist folder with static site ready to host
uv python incept.py build

# clean the dist
uv python incept.py build

# add new post file
uv python incept.py new [post_name]

# serve the dist folder (with hotreload)
uv python incept.py serve
```
