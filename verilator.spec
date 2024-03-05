Name:           verilator
Version:        5.022
Release:        %autorelease
Summary:        A fast simulator for synthesizable Verilog
License:        LGPL-3.0-only OR Artistic-2.0
URL:            https://veripool.org/verilator/
Source0:        https://github.com/verilator/verilator/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
BuildRequires:  autoconf
BuildRequires:  bison
BuildRequires:  coreutils
BuildRequires:  cmake
BuildRequires:  findutils
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  help2man
BuildRequires:  make
BuildRequires:  perl
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  python3-devel
BuildRequires:  sed

Requires:       perl

# required for further tests
BuildRequires:  gdb

# Backported from upstream to fix building
Patch0:  0001-fix-try-lock-spuriously-fails.patch

# Sent upstream through GitHub
Patch1:  0002-Allow-for-custom-verilator-revision-in-version-check.patch

%description
Verilator is the fastest free Verilog HDL simulator. It compiles
synthesizable Verilog, plus some PSL, SystemVerilog and Synthesis
assertions into C++ or SystemC code. It is designed for large projects
where fast simulation performance is of primary concern, and is
especially well suited to create executable models of CPUs for
embedded software design teams.

%prep
%autosetup -p1

find . -name .gitignore -delete
export VERILATOR_ROOT=%{_datadir}
autoconf
%{configure} \
    --disable-ccwarn \
    --disable-longtests

# We cannot run autoreconf because upstream uses unqualifed stdlib identifiers
# that are included by autoconf-generated header files.
find -name Makefile_obj -exec sed -i \
    -e 's|^\(COPT = .*\)|\1 %{optflags}|' \
    -e 's|^#LDFLAGS += .*|LDFLAGS += %{__global_ldflags}|' \
    {} \;

%build
export VERILATOR_CUSTOM_REV=fedora-%{version}
%make_build 

%check
make test 

%install
%make_install

# remove the copy of examples in the datadir so we could
# mark the copy in the source directory as "doc"
rm -rf %{buildroot}%{_datadir}/verilator/examples

# remove not needed build directory and bin directory
rm -rf %{buildroot}%{_datadir}/verilator/src
rm -rf %{buildroot}%{_bindir}/verilator_includer

# verilator installs verilator.pc under ${datadir}
# but for consistency we want it under ${libdir}
mkdir -p %{buildroot}%{_libdir}/pkgconfig
mv %{buildroot}%{_datadir}/pkgconfig/verilator.pc %{buildroot}%{_libdir}/pkgconfig


%files
%license Artistic LICENSE
%doc Changes README*
%doc docs/
%doc examples/
%{_mandir}/man1/*.1.gz
%{_datadir}/verilator
%{_libdir}/pkgconfig/verilator.pc
%{_bindir}/verilator
%{_bindir}/verilator_bin
%{_bindir}/verilator_bin_dbg
%{_bindir}/verilator_coverage
%{_bindir}/verilator_coverage_bin_dbg
%{_bindir}/verilator_gantt
%{_bindir}/verilator_profcfunc


%changelog
%autochangelog
