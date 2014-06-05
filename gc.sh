echo
echo "CubicERP/branch"
git checkout $1
cd odoo
echo
echo "CubicERP/odoo"
git checkout $1
cd ../trunk
echo
echo "CubicERP/trunk"
git checkout $1
cd ..
