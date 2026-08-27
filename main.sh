#!/bin/bash
# Clean public directory and copy static files
rm -rf public
echo "public removed"
mkdir public
echo "public created"  
cp -r static/ public/
echo "static copied to public"  

# Run your site generator
python3 src/main.py
echo "main successful"  

# Serve the site
cd public 
echo "cd to public"  
python3 -m http.server 8888
