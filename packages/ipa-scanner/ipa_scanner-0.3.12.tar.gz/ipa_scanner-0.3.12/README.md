# ipa-scanner

A Python automation tool for downloading SAP IPA BOM data using Selenium.

# Node Publish

pyinstaller ipa_scanner/main.py --name ipa-scan --onefile

chmod +x bin/ipa-scan   

echo "registry=https://registry.npmjs.org/" > .npmrc

npm login
npm publish

ipa-scan


# Pypi Publish

pip install --upgrade build twine

python -m build

twine upload dist/*


