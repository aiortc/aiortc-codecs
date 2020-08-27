set destdir=%1

set outputfile=output\codecs-win%PYTHON_ARCH%.tar.gz
if "%PYTHON_ARCH%" == "64" (
    set triplet=x64-windows-static
) else (
    set triplet=x86-windows-static
)

vcpkg install libvpx:%triplet% opus:%triplet%

if exist %destdir% (
    rmdir /s /q %destdir%
)
mkdir %destdir%
mkdir %destdir%\include
mkdir %destdir%\lib
xcopy C:\vcpkg\installed\%triplet%\include %destdir%\include\ /E
xcopy C:\vcpkg\installed\%triplet%\lib %destdir%\lib\ /E

if not exist output (
    mkdir output
)
tar czvf %outputfile% -C %destdir% include lib
