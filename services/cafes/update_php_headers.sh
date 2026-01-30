#!/bin/bash
# Script to add GPL2 headers to CAFES PHP files

CAFES_DIR="/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/public"

for file in "$CAFES_DIR"/*.php; do
    if [ -f "$file" ]; then
        basename=$(basename "$file")
        
        # Check if already has GPL header
        if ! grep -q "GPL-2.0" "$file"; then
            echo "Updating: $basename"
            
            # Create temp file with header + original content (skip first <?php line)
            {
                echo "<?php"
                echo "/**"
                echo " * ================================================================================"
                echo " * PROYECTO: CAFES - Sistema de Planes de Negocio"
                echo " * ARCHIVO:  public/$basename"
                echo " * COPYRIGHT: © 2026 Fondo Thoth AC."
                echo " * LICENCIA: GPL-2.0-or-later"
                echo " * ================================================================================"
                echo " */"
                echo ""
                # Skip first line if it's <?php
                tail -n +2 "$file"
            } > "$file.tmp"
            
            mv "$file.tmp" "$file"
        else
            echo "Skipping (already has GPL): $basename"
        fi
    fi
done

echo ""
echo "Done! PHP files updated with GPL2 headers."
