Summary:	AppleTalk networking programs
Summary(pl):	Klient i serwer AppleTalk
Name:		netatalk
Version:	1.4b2+asun2.1.3
Release:	15
License:	BSD
Group:		Daemons
Group(de):	Server
Group(pl):	Serwery
Source0:	ftp://download.sourceforge.net/pub/sourceforge/netatalk/%{name}-%{version}.tar.gz
Source1:	atalk.init
Source2:	%{name}.config
Source3:	AppleVolumes.system
Source4:	ICDumpSuffixMap
Patch0:		%{name}-asun.fsstnd.patch
Patch1:		%{name}-asun.install.patch
Patch2:		%{name}-asun.librpcsvc.patch
Patch3:		%{name}-asun.nbp.patch
Patch4:		%{name}-pam.patch
#Patch5:	linux-2.4-quota.patch
URL:		http://www.umich.edu/~rsug/netatalk/
Prereq:		/sbin/chkconfig
BuildRequires:	pam-devel
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
%patch -p1 -b .fsstnd
%patch1 -p1 -b .install
#if [ ! -e "/usr/lib/librpcsvc.a" ]; then
%patch2 -p1 -b .rpcsvc
#fi
%patch3 -p1 -b .nbp
%patch4 -p1 -b .pam
#%patch5 -p1 -b .redhat

%build
rm -f "etc/papd/.#magics.c"
rm -f "etc/.#diff"

#%ifarch alpha 
#	make 
#%else
#	make OPTOPTS="$RPM_OPT_FLAGS -fomit-frame-pointer -fsigned-char"
#%endif
%{__make} OPTOPTS=""

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/{rc.d/init.d,pam.d,security,sysconfig,atalk/uams} \
	$RPM_BUILD_ROOT%{_libdir}/atalk \
	$RPM_BUILD_ROOT%{_mandir}/{man1,man3,man4,man8}                         


%{__make} install INSTALL_PREFIX=$RPM_BUILD_ROOT MANDIR=$RPM_BUILD_ROOT%{_mandir}

(
  cd $RPM_BUILD_ROOT%{_libdir}/atalk/filters/
  for i in * ; do
ln -sf %{_sbindir}/psf $i
  done
)

install config/AppleVolumes.default $RPM_BUILD_ROOT%{_sysconfdir}/atalk/AppleVolumes.default
install config/afpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/atalk/afpd.conf
install config/atalkd.conf $RPM_BUILD_ROOT%{_sysconfdir}/atalk/atalkd.conf
install config/papd.conf $RPM_BUILD_ROOT%{_sysconfdir}/atalk/papd.conf
install  config/netatalk.pamd $RPM_BUILD_ROOT/etc/pam.d/netatalk

install %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/atalk
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/netatalk
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/atalk/AppleVolumes.system

install ${RPM_SOURCE_DIR}/ICDumpSuffixMap .

> $RPM_BUILD_ROOT/etc/security/blacklist.netatalk

mv -f etc/afpd/uam/README README.uam

gzip -9nf BUGS CHANGES COPYRIGHT ChangeLog ICDu* \
	README* TODO VERSION services.atalk INSTALL/*


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
%doc {BUGS,CHANGES,COPYRIGHT,ChangeLog,README*,TODO,VERSION,services.atalk,ICDumpSuffixMap}.gz INSTALL 

%dir %{_sysconfdir}/atalk
%dir %{_sysconfdir}/atalk/uams
%config(noreplace) %verify(not size mtime md5)%{_sysconfdir}/atalk/AppleVolumes.default
%config(noreplace) %verify(not size mtime md5)%{_sysconfdir}/atalk/AppleVolumes.system
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/netatalk
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/afpd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/atalkd.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/atalk/papd.conf

%attr(755,root,root) %config %{_initdir}/atalk
%attr(640,root,root) %config %verify(not size mtime md5) /etc/pam.d/netatalk
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/security/blacklist.netatalk

%attr(755,root,root) %{_sbindir}/afpd
%attr(755,root,root) %{_sbindir}/atalkd
%attr(755,root,root) %{_sbindir}/etc2ps
%attr(755,root,root) %{_sbindir}/papd
%attr(755,root,root) %{_sbindir}/psa
%attr(755,root,root) %{_sbindir}/psf

%attr(755,root,root) %{_bindir}/adv1tov2
%attr(755,root,root) %{_bindir}/aecho
%attr(755,root,root) %{_bindir}/getzones
%attr(755,root,root) %{_bindir}/megatron
%attr(755,root,root) %{_bindir}/nbplkup
%attr(755,root,root) %{_bindir}/nbprgstr
%attr(755,root,root) %{_bindir}/nbpunrgstr
%attr(755,root,root) %{_bindir}/pap
%attr(755,root,root) %{_bindir}/papstatus
%attr(755,root,root) %{_bindir}/psorder
%attr(755,root,root) %{_bindir}/hqx2bin
%attr(755,root,root) %{_bindir}/macbinary
%attr(755,root,root) %{_bindir}/single2bin
%attr(755,root,root) %{_bindir}/unbin
%attr(755,root,root) %{_bindir}/unhex
%attr(755,root,root) %{_bindir}/unsingle

%dir %{_libdir}/atalk/
%{_mandir}/*/*

%files devel
%defattr(644,root,root,755)
%{_libdir}/libatalk.a
%{_libdir}/libatalk_p.a
%{_includedir}/atalk
%{_includedir}/netatalk
