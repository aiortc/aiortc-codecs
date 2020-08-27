#!/bin/sh

set -xe

if [ -z "$1" ]; then
    echo "Usage: $0 <prefix>"
    exit 1
fi

destdir=$1

builddir=`pwd`/build
sourcedir=`pwd`/source

for d in $builddir $destdir; do
    if [ -e $d ]; then
        rm -rf $d
    fi
done

extract() {
    path=$builddir/$1
    url=$2
    tarball=$sourcedir/`echo $url | sed -e 's/.*\///'`

    if [ ! -e $tarball ]; then
        curl -L -o $tarball $url
    fi

    mkdir $path
    tar xf $tarball -C $path --strip-components 1
}

if [ "`uname`" = "Linux" ]; then
    outputdir=/output
    outputfile=$outputdir/codecs-manylinux_$(uname -m).tar.gz
elif [ "`uname`" = "Darwin" ]; then
    outputdir=`pwd`/output
    outputfile=$outputdir/codecs-macosx_$(uname -m).tar.gz
else
    echo "Unknown platform"
    exit 1
fi

mkdir -p $outputdir
if [ ! -e $outputfile ]; then
    mkdir $builddir
    mkdir -p $sourcedir
    cd $builddir

    # build vpx
    extract vpx https://github.com/webmproject/libvpx/archive/v1.9.0.tar.gz
    cd vpx
    ./configure --prefix=$destdir --disable-examples --disable-tools --disable-unit-tests --enable-pic
    make -j
    make install
    cd ..

    # build opus
    extract opus https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz
    cd opus
    ./configure --prefix=$destdir --disable-shared --enable-static --with-pic
    make -j
    make install
    cd ..

    tar czvf $outputfile -C $destdir include lib
fi
