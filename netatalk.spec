Summary:	AppleTalk networking programs
Summary(pl):	Klient i serwer AppleTalk
Summary(pt_BR):	Programas para rede AppleTalk
Summary(zh_CN):	Appletalk 和 Appleshare/IP 服务工具
Name:		netatalk
Version:	1.6.3
Release:	2
Epoch:		2
License:	BSD
Group:		Daemons
Source0:	http://dl.sourceforge.net/netatalk/%{name}-%{version}.tar.bz2
# Source0-md5:	fa3d0e08499525d9a627fe17a2d93d1b
Source1:	%{name}.init
Source2:	%{name}.pamd
Source3:	%{name}.sysconfig
Source4:	ICDumpSuffixMap
Patch0:		%{name}-no_libnsl.patch
URL:		http://www.umich.edu/~rsug/netatalk/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cracklib-devel
BuildRequires:	db-devel
BuildRequires:	gettext-devel
BuildRequires:	libtool
BuildRequires:	openssl-devel >= 0.9.7
BuildRequires:	pam-devel
Requires(post,preun):	/sbin/chkconfig
Requires(post):	/sbin/ldconfig
Requires:	pam >= 0.77.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package enables Linux to talk to Macintosh computers via the
AppleTalk networking protocol. It includes a daemon to allow Linux to
act as a file server over EtherTalk or IP for Mac's.

%description -l pl
Pakiet ten pozwala na komunikacje kumputer體 OS Linux z Macintosh za
po秗ednictwem protoko硊 AppleTalk. Uczyni twojego Linux-a serwerem
oraz klienta plik體 i wydruk體 zar體no za po秗ednictwem protoko硊
EtherTalk jaki IP for Mac's.

%description -l pt_BR
Este pacote habilita o Linux a servir computadores Macintosh atrav閟
do protocolo AppleTalk.

%package devel
Summary:	Headers and static libraries for Appletalk development
Summary(pl):	Pliki nag丑wkoew i biblioteki statyczne Appletalk
Summary(pt_BR):	Arquivos de inclus鉶 e bibliotecas para o desenvolvimento de aplicativos baseados no protocolo AppleTalk
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}

%description devel
This packge contains the header files, and static libraries for
building Appletalk networking programs.

%description devel -l pl
Pakiet ten zawiera pliki nag丑wkowe i biblioteki statyczne serwera
AppleTalk

%description devel -l pt_BR
Arquivos de inclus鉶 e bibliotecas para o desenvolvimento de
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
        --enable-pgp-uam

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/{rc.d/init.d,pam.d,security,sysconfig,atalk/msg,atalk/nls} \
	$RPM_BUILD_ROOT%{_libdir}/atalk \
	$RPM_BUILD_ROOT%{_mandir}/{man1,man3,man4,man8}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	m4datadir=%{_aclocaldir}

install etc/afpd/nls/{makecode,parsecode} $RPM_BUILD_ROOT%{_bindir}

install %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/atalk
install %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/netatalk
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/netatalk
install %{SOURCE4} .

> $RPM_BUILD_ROOT/etc/security/blacklist.netatalk

# to avoid conflict with glibc-devel
rm -f $RPM_BUILD_ROOT%{_includedir}/atalk/at.h
rm -f $RPM_BUILD_ROOT%{_includedir}/netatalk/at.h

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add atalk
if [ "$1" = "1" ] ; then
	echo "Run \"%{_initrddir}/atalk start\" to start netatalk." >&2
fi

%preun
if [ "$1" = "0" ]; then
	%{_initrddir}/atalk stop >&2
	/sbin/chkconfig --del atalk
fi

%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog ICDu* NEWS README TODO VERSION services.atalk doc
%dir %{_sysconfdir}/atalk/msg
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/nls/*
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/AppleVolumes.default
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/AppleVolumes.system
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/netatalk
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/afpd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/atalkd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/papd.conf

%attr(755,root,root) %config %{_initrddir}/atalk
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/pam.d/netatalk
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/security/blacklist.netatalk

%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/[!n]*
%attr(755,root,root) %{_bindir}/n[!e]*
%attr(755,root,root) %{_bindir}/netatalkshorternamelinks.pl
%attr(755,root,root) %{_libdir}/atalk/*.so
%{_mandir}/*/*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/netatalk-config
%attr(644,root,root) %{_libdir}/libatalk.a
%{_libdir}/libatalk.la
%{_libdir}/atalk/*.a
%{_libdir}/atalk/*.la
%{_includedir}/atalk
%{_includedir}/netatalk/*
%{_aclocaldir}/*
