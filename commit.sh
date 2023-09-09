#!/usr/bin/env sh

set -e

git init
git add .
git commit -m '部署重构'


# 如果发布到 https://<USERNAME>.github.io/<REPO>
git push -f git@github.com:konelane/QQbot_Kal-tsit.git master

cd -