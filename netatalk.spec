# versions of required libraries
Summary:	AppleTalk networking programs
Summary(pl.UTF-8):	Klient i serwer AppleTalk
Summary(pt_BR.UTF-8):	Programas para rede AppleTalk
Summary(zh_CN.UTF-8):	Appletalk 和 Appleshare/IP 服务工具
Name:		netatalk
Version:	3.0
Release:	1
Epoch:		2
License:	BSD
Group:		Daemons
Source0:	http://download.sourceforge.net/netatalk/%{name}-%{version}.tar.bz2
# Source0-md5:	62eb034011bb60b0bfd95072af3693dc
Source1:	%{name}.init
Source2:	%{name}.pamd
Source3:	%{name}.sysconfig
Source4:	ICDumpSuffixMap
Patch0:		%{name}-build.patch
URL:		http://www.umich.edu/~rsug/netatalk/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cracklib-devel
BuildRequires:	db-devel >= 4.6.0
BuildRequires:	gettext-devel
BuildRequires:	libevent-devel
BuildRequires:	libltdl-devel
BuildRequires:	libtool
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires:	libgcrypt >= 1.4.5
Requires:	pam >= 0.99.7.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package enables Linux to talk to Macintosh computers via the
AppleTalk networking protocol. It includes a daemon to allow Linux to
act as a file server over EtherTalk or IP for Mac's.

%description -l pl.UTF-8
Pakiet ten pozwala na komunikację komputerów OS Linux z Macintosh za
pośrednictwem protokołu AppleTalk. Uczyni twojego Linux-a serwerem
oraz klientem plików i wydruków zarówno za pośrednictwem protokołu
EtherTalk jaki IP for Mac's.

%description -l pt_BR.UTF-8
Este pacote habilita o Linux a servir computadores Macintosh através
do protocolo AppleTalk.

%package devel
Summary:	Headers and static libraries for Appletalk development
Summary(pl.UTF-8):	Pliki nagłówkoew i biblioteki statyczne Appletalk
Summary(pt_BR.UTF-8):	Arquivos de inclusão e bibliotecas para o desenvolvimento de aplicativos baseados no protocolo AppleTalk
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}

%description devel
This packge contains the header files, and static libraries for
building Appletalk networking programs.

%description devel -l pl.UTF-8
Pakiet ten zawiera pliki nagłówkowe i biblioteki statyczne serwera
AppleTalk.

%description devel -l pt_BR.UTF-8
Arquivos de inclusão e bibliotecas para o desenvolvimento de
aplicativos baseados no protocolo AppleTalk.

%prep
%setup -q
%patch0 -p1

%build
rm -f missing
%{__libtoolize}
%{__aclocal} -I macros
%{__autoconf}
%{__automake}
%{__autoheader}
%configure \
	--with-config-dir=%{_sysconfdir}/atalk \
	--with-pkgconfdir=%{_sysconfdir}/atalk \
	--with-uams-path=%{_libdir}/atalk \
	--with-msg-dir=%{_sysconfdir}/atalk/msg \
	--enable-lastdid \
	--enable-timelord \
	--with-cracklib=%{_datadir}/dict/cracklib_dict \
	--with-pam \
	--with-shadow \
	--with-tcp-wrappers \
	--with-ssl \
	--enable-pgp-uam \
	--disable-bundled-libevent

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,pam.d,security,sysconfig,atalk/msg} \
	$RPM_BUILD_ROOT%{_libdir}/atalk \
	$RPM_BUILD_ROOT%{_mandir}/{man1,man3,man4,man8}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	m4datadir=%{_aclocaldir}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/atalk
install %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/netatalk
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/netatalk
install %{SOURCE4} .

> $RPM_BUILD_ROOT/etc/security/blacklist.netatalk

# to avoid conflict with glibc-devel
rm -f $RPM_BUILD_ROOT%{_includedir}/atalk/at.h
rm -f $RPM_BUILD_ROOT%{_includedir}/netatalk/at.h
# to avoid conflict with coreutils-7.1
rm -f $RPM_BUILD_ROOT%{_bindir}/timeout

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add atalk
if [ "$1" = "1" ] ; then
	echo "Run \"/etc/rc.d/init.d/atalk start\" to start netatalk." >&2
fi

%preun
if [ "$1" = "0" ]; then
	/etc/rc.d/init.d/atalk stop >&2
	/sbin/chkconfig --del atalk
fi

%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ICDu* NEWS VERSION doc
%dir %{_sysconfdir}/atalk
%dir %{_sysconfdir}/atalk/msg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/atalk/afp.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/netatalk

%attr(755,root,root) %config /etc/rc.d/init.d/atalk
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/pam.d/netatalk
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/security/blacklist.netatalk

%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/[!n]*
%attr(755,root,root) %{_libdir}/libatalk.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libatalk.so.1
%dir %{_libdir}/atalk
%attr(755,root,root) %{_libdir}/atalk/*.so
%{_mandir}/*/*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/netatalk-config
%attr(755,root,root) %{_libdir}/libatalk.so
%{_libdir}/libatalk.a
%{_libdir}/libatalk.la
%{_libdir}/atalk/*.a
%{_libdir}/atalk/*.la
%{_includedir}/atalk
%{_aclocaldir}/*
