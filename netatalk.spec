Summary:	AppleTalk networking programs
Summary(pl):	Klient i serwer AppleTalk
Name:		netatalk
Version:	1.5pre8
Release:	1
License:	BSD
Group:		Daemons
Group(de):	Server
Group(pl):	Serwery
Source0:	ftp://download.sourceforge.net/pub/sourceforge/netatalk/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.pamd
Source3:	%{name}.sysconfig
Source4:	ICDumpSuffixMap
Patch0:         %{name}-configure.patch
URL:		http://www.umich.edu/~rsug/netatalk/
Prereq:		/sbin/chkconfig
BuildRequires:	pam-devel
BuildRequires:	openssl-devel
BuildRequires:	db3-devel
BuildRequires:	cracklib-devel
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	libtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define _initdir /etc/rc.d/init.d 

%description
This package enables Linux to talk to Macintosh computers via the
AppleTalk networking protocol. It includes a daemon to allow Linux to
act as a file server over EtherTalk or IP for Mac's.

%description -l pl
Pakiet ten pozwala na komunikacje kumputerów OS Linux z Macintosh za
po¶rednictwem protoko³u AppleTalk. Uczyni twojego Linux-a serwerem
oraz klienta plików i wydruków zarówno za po¶rednictwem protoko³u
EtherTalk jaki IP for Mac's.

%package devel
Summary:	Headers and static libraries for Appletalk development
Summary(pl):	Pliki nag³ówkoew i biblioteki statyczne Appletalk
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Requires:	%{name} = %{version}

%description devel
This packge contains the header files, and static libraries for
building Appletalk networking programs.

%description -l pl devel
Pakiet ten zawiera pliki nag³ówkowe i biblioteki statyczne serwera
AppleTalk


%prep
%setup -q
%patch0 -p1

%build
rm -f missing
gettextize --copy --force
libtoolize --copy --force
aclocal
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
        --with-cracklib \
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


%{__make} install DESTDIR=$RPM_BUILD_ROOT MANDIR=$RPM_BUILD_ROOT%{_mandir}

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

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add atalk
ldconfig
# Do only for the first install
if [ "$1" = 1 ] ; then
  # Add the ddp lines to /etc/services
  if (grep '[0-9][0-9]*/ddp' /etc/services >/dev/null); then
    cat <<'_EOD1_' >&2
warning:	The DDP services appear to be present in /etc/services.
warning:	Please check them against services.atalk in the documentation.
_EOD1_
    true
  else
    cat <<'_EOD2_' >>/etc/services
# start of DDP services
#
# Everything between the 'start of DDP services' and 'end of DDP services'
# lines will be automatically deleted when the netatalk package is removed.
#
rtmp		1/ddp		# Routing Table Maintenance Protocol
nbp		2/ddp		# Name Binding Protocol
echo		4/ddp		# AppleTalk Echo Protocol
zip		6/ddp		# Zone Information Protocol

afpovertcp	548/tcp		# AFP over TCP
afpovertcp	548/udp
# end of DDP services
_EOD2_
  fi
fi
    echo "Run \"/etc/rc.d/init.d/atalk start\" to start netatalk." >&2
	
%preun
if [ "$1" = "0" ]; then
/etc/rc.d/init.d/atalk stop >&2
fi

if [ "$1" = "0" ] ; then
  %{_initdir}/atalk stop > /dev/null 2>&1
  /sbin/chkconfig --del atalk
  # remove the ddp lines from /etc/services
  if (grep '^# start of DDP services$' /etc/services >/dev/null && \
      grep '^# end of DDP services$' /etc/services >/dev/null ); then
    sed -e '/^# start of DDP services$/,/^# end of DDP services$/d' \
	</etc/services >/tmp/services.tmp$$
    cat /tmp/services.tmp$$ >/etc/services
    rm -f /tmp/services.tmp$$
  else
    cat <<'_EOD3_' >&2
warning:	Unable to find the lines `# start of DDP services' and
warning:	`# end of DDP services' in the file /etc/services.
warning:	You should remove the DDP services from /etc/service manually.
_EOD3_
  fi
fi


%files
%defattr(644,root,root,755)
%doc {BUGS,CHANGES,COPYRIGHT,ChangeLog,README,TODO,VERSION,services.atalk,ICDumpSuffixMap}.gz doc/*

%dir %{_sysconfdir}/atalk/msg
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/nls/*
%config(noreplace) %verify(not size mtime md5)%{_sysconfdir}/atalk/AppleVolumes.default
%config(noreplace) %verify(not size mtime md5)%{_sysconfdir}/atalk/AppleVolumes.system
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/netatalk
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/afpd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/atalkd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/papd.conf

%attr(755,root,root) %config %{_initdir}/atalk
%attr(640,root,root) %config %verify(not size mtime md5) /etc/pam.d/netatalk
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/security/blacklist.netatalk

%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/atalk/*.so
%{_mandir}/*/*

%files devel
%defattr(644,root,root,755)
%attr(644,root,root) %{_libdir}/libatalk.a
%attr(755,root,root) %{_libdir}/libatalk.la
%attr(644,root,root) %{_libdir}/atalk/*.a
%attr(755,root,root) %{_libdir}/atalk/*.la
%{_includedir}/atalk
%{_includedir}/netatalk
