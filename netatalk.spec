Summary:	AppleTalk networking programs
Summary(pl):	Klient i serwer AppleTalk
Summary(pt_BR):	Programas para rede AppleTalk
Name:		netatalk
Version:	1.5.0
Release:	2
License:	BSD
Group:		Daemons
Source0:	ftp://download.sourceforge.net/pub/sourceforge/netatalk/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.pamd
Source3:	%{name}.sysconfig
Source4:	ICDumpSuffixMap
Patch0:		%{name}-makefile-am.patch
URL:		http://www.umich.edu/~rsug/netatalk/
Prereq:		/sbin/chkconfig
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cracklib-devel
BuildRequires:	db3-devel
BuildRequires:	libtool
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:  gettext-devel
BuildRequires:  glibc-static
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_initdir	/etc/rc.d/init.d

%description
This package enables Linux to talk to Macintosh computers via the
AppleTalk networking protocol. It includes a daemon to allow Linux to
act as a file server over EtherTalk or IP for Mac's.

%description -l pl
Pakiet ten pozwala na komunikacje kumputerów OS Linux z Macintosh za
po¶rednictwem protoko³u AppleTalk. Uczyni twojego Linux-a serwerem
oraz klienta plików i wydruków zarówno za po¶rednictwem protoko³u
EtherTalk jaki IP for Mac's.

%description -l pt_BR
Este pacote habilita o Linux a servir computadores Macintosh através
do protocolo AppleTalk.

%package devel
Summary:	Headers and static libraries for Appletalk development
Summary(pl):	Pliki nag³ówkoew i biblioteki statyczne Appletalk
Summary(pt_BR):	Arquivos de inclusão e bibliotecas para o desenvolvimento de aplicativos baseados no protocolo AppleTalk
Group:		Development/Libraries
Requires:	%{name} = %{version}

%description devel
This packge contains the header files, and static libraries for
building Appletalk networking programs.

%description devel -l pl
Pakiet ten zawiera pliki nag³ówkowe i biblioteki statyczne serwera
AppleTalk

%description devel -l pt_BR
Arquivos de inclusão e bibliotecas para o desenvolvimento de
aplicativos baseados no protocolo AppleTalk.

%prep
%setup -q
%patch0 -p1

%build
rm -f missing
gettextize --copy --force
libtoolize --copy --force
aclocal -I macros
autoconf
automake -a -c
autoheader
%configure \
	--with-config-dir=%{_sysconfdir}/atalk \
	--with-pkgconfdir=%{_sysconfdir}/atalk \
	--with-uams-path=%{_libdir}/atalk \
	--with-msg-dir=%{_sysconfdir}/atalk/msg \
	--enable-lastdid \
	--enable-timelord \
        --with-cracklib=%{_datadir}/dict \
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

install etc/afpd/nls/{makecode,parsecode} $RPM_BUILD_ROOT/%{_bindir}

install %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/atalk
install %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/netatalk
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/netatalk
install %{SOURCE4} .

> $RPM_BUILD_ROOT/etc/security/blacklist.netatalk

gzip -9nf BUGS CHANGES COPYRIGHT ChangeLog ICDu* \
	NEWS README TODO VERSION services.atalk doc/*

# to avoid conflict with glibc-devel
rm -f $RPM_BUILD_ROOT%{_includedir}/atalk/at.h
rm -f $RPM_BUILD_ROOT%{_includedir}/netatalk/at.h

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add atalk
ldconfig
if [ "$1" = 1 ] ; then
	echo "Run \"%{_initdir}/atalk start\" to start netatalk." >&2
fi

%preun
if [ "$1" = "0" ]; then
	%{_initdir}/atalk stop >&2
fi

%files
%defattr(644,root,root,755)
%doc *.gz doc/*
%dir %{_sysconfdir}/atalk/msg
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/nls/*
%config(noreplace) %verify(not size mtime md5)%{_sysconfdir}/atalk/AppleVolumes.default
%config(noreplace) %verify(not size mtime md5)%{_sysconfdir}/atalk/AppleVolumes.system
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/netatalk
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/afpd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/atalkd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/papd.conf

%attr(755,root,root) %config %{_initdir}/atalk
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/pam.d/netatalk
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/security/blacklist.netatalk

%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/atalk/*.so
%{_mandir}/*/*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/netatalk-config
%attr(644,root,root) %{_libdir}/libatalk.a
%attr(755,root,root) %{_libdir}/libatalk.la
%attr(644,root,root) %{_libdir}/atalk/*.a
%attr(755,root,root) %{_libdir}/atalk/*.la
%{_includedir}/atalk
%{_includedir}/netatalk
%{_aclocaldir}/*
