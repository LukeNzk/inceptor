# Inceptor blog generator

Tool to generate static blog website, that with lightspeed loadtime.

# Usage
```sh
# generates dist folder with static site ready to host
uv python build.py build

# clean the dist
uv python build.py build

# add new post file
uv python build.py new [post_name]

# serve the dist folder (with hotreload)
uv python build.py serve
```
