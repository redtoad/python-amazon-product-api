#!/bin/sh
# Using hg-git to work in git and push to hg
# http://traviscline.com/blog/2010/04/27/using-hg-git-to-work-in-git-and-push-to-hg/

BITBUCKET=ssh://hg@bitbucket.org/basti/python-amazon-product-api
GITHUB=ssh://git@github.com/redtoad/python-amazon-product-api

TMPREPO=`mktemp --directory --suffix=amazon`

# Here are the basic steps I follow to get set up to work with git on an hg
# project. First, we need a mercurial checkout.
hg clone $BITBUCKET $TMPREPO
cd $TMPREPO

# Before we create the git repo let’s create bookmarks for the hg branches we
# would like to interact with in git (this can be done after the initial
# gexport as well).
# I’m prefixing the refs with hg so we have slight namespace separation between
# our git branches and the refs that are updated with gexport
branches=`hg branches --active|awk '{print $1};'`
for branch in $branches; do
    hg bookmark hg/$branch -r $branch
done

# hg-git init’s a bare repo, for now create your .git with 
git init

# Ok. Let’s go ahead and create the git repo:
hg gexport

# By default gexport will create the git repo at .hg/git. I prefer my .git and
# .hg directories to live side-by-side. Just simply symlink the .git repo into
# the right place:
ln -s .hg/git .git

# From here let’s create a branch corresponding to the “hg” branch:
for branch in $branches; do
    git branch $branch hg/$branch
done

# And make our master the same as hg/default:
git reset hg/default

# From here you can make commits on your git branches and pull them into your
# hg repo with:
hg gimport

# Subsequent pulls/fetches and gexport calls will push new commits to the hg/
# refs in git.

# There you go! A push from there would get your git commits to your remote hg
# repo. You’re set up to work with git and publish to hg!
git push $GITHUB

