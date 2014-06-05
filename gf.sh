echo
echo "CubicERP/branch"
git fetch
git merge origin
cd odoo
echo
echo "CubicERP/odoo"
git fetch
git merge origin
cd ../trunk
echo
echo "CubicERP/trunk"
git fetch
git merge origin
cd ..
