Name:           verilator
Version:        3.712
Release:        1%{?dist}
Summary:        A fast simulator for synthesizable Verilog
License:        GPLv2
Group: 	        Applications/Engineering
URL:            http://www.veripool.com/verilator.html
Source0:        http://www.veripool.org/verilator/ftp/%{name}-%{version}.tgz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  perl, flex, bison, perl-SystemPerl-devel
Requires:       perl-SystemPerl-devel >= 1.320
Patch0:         verilator-driver.patch

%description

Verilator is the fastest free Verilog HDL simulator. It compiles
synthesizable Verilog, plus some PSL, SystemVerilog and Synthesis
assertions into C++ or SystemC code. It is designed for large projects
where fast simulation performance is of primary concern, and is
especially well suited to create executable models of CPUs for
embedded software design teams.

Authors:
--------

Wilson Snyder
Paul Wasson
Duane Galbi

%prep
%setup -q
%patch0 -p1
find . -name .gitignore -exec rm {} \;
export VERILATOR_ROOT=%{_datadir}
%{configure} --enable-envdef --prefix=%{_prefix} --mandir=%{_mandir} 
%{__sed} -i "s|CPPFLAGSNOWALL +=|CPPFLAGSNOWALL +=%{optflags}|" \
{src,test_c,test_regress,test_sc,test_sp,test_verilated}/Makefile_obj

%build
SYSTEMPERL_INCLUDE=%{_includedir}/perl-SystemPerl %{__make} %{?_smp_mflags} 


%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=$RPM_BUILD_ROOT install

# move the examples out of the datadir so that we can later include
# them in the doc dir
%{__mv} %{buildroot}%{_datadir}/verilator/examples examples

# remove not needed build directory and bin directory
%{__rm} -rf %{buildroot}%{_datadir}/verilator/src
%{__rm} -rf %{buildroot}%{_bindir}/verilator_includer

%clean
%{__rm} -rf %{buildroot}  

%files

%defattr(-, root, root, -)
%doc README
%doc COPYING Changes TODO Artistic
%doc verilator.pdf verilator.html
%doc examples/

%attr(644,-,-) %{_mandir}/man1/verilator.1.gz
%{_datadir}/verilator

%{_bindir}/verilator
%{_bindir}/verilator_bin
%{_bindir}/verilator_bin_dbg
%{_bindir}/verilator_profcfunc


%changelog

* Fri Jul 24 2009 Lane Brooks <dirjud [AT] gmail DOT com> - 3.712-1
- Updated to verilator 3.712

* Fri Jun 26 2009 Lane Brooks <dirjud [AT] gmail DOT com> - 3.711-1
- Updated to verilator 3.711
- Added Artistic file
- Fixed permissions on man file 

* Tue Jun 9 2009 Lane Brooks <dirjud [AT] gmail DOT com> - 3.710-1
- Updated to verilator 3.710
- Removed GCC 4.3 patch (no longer necessary)
- Added SYSTEMPERL_INCLUDE to point to perl-SystemPerl rpm install location

* Fri Jan 9 2009 Lane Brooks <dirjud [AT] gmail DOT com> - 3.700-1
- Updated dependancy to newly packaged perl-SystemPerl and removed patch
- Updated to verilator 3.700
- Added GCC 4.3 patch

* Fri Jan 2 2009 Lane Brooks <dirjud [AT] gmail DOT com> - 3.681-2
- Moved examples from data dir to doc dir

* Thu Jan 1 2009 Lane Brooks <dirjud [AT] gmail DOT com> - 3.681-1
- Updated verilator 3.681
- Removed gcc 4.3 patch as verilator 3.681 incorporates this fix
- Removed shared object patch as it is possible to do this from Makefile
  using environment variables
- Further updates to the spec file per Chitlesh's feedback

* Sun Oct 26 2008 Lane Brooks <dirjud [AT] gmail DOT com> - 3.680-3
- Improved spec file for Fedora integration based on initial feedback

* Thu Oct 23 2008 Lane Brooks <dirjud [AT] gmail DOT com> - 3.680-2
- Added shared object generation patch

* Thu Oct 16 2008 Lane Brooks <dirjud [AT] gmail DOT com> - 3.680-1
- Initial package based on SUSE packages from Guenter Dannoritzer <dannoritzer{%}web{*}de>
