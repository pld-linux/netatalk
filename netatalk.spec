Summary:	AppleTalk networking programs
Summary(pl):	Klient i serwer AppleTalk
Name:		netatalk
Version:	1.4b2+asun2.1.3
Release:	15
License:	BSD
Group:		System Environment/Daemons
Group(pl):      Sieciowe/Serwery
Source0:	ftp://ftp.u.washington.edu/public/asun/netatalk-1.4b2+asun2.1.3.tar.gz
Source1:	atalk.init
Source2:	netatalk.config
Source3:	AppleVolumes.system
Source4:	ICDumpSuffixMap
Patch:		netatalk-asun.fsstnd.patch
Patch1:		netatalk-asun.install.patch
Patch2:		netatalk-asun.librpcsvc.patch
Patch3:		netatalk-asun.nbp.patch
Patch4:		netatalk-pam.patch
#Patch5:		linux-2.4-quota.patch
Prereq:		/sbin/chkconfig, /etc/rc.d/init.d
Requires:	pam >= 0.56
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define _initdir /etc/rc.d/init.d 

%description
This package enables Linux to talk to Macintosh computers via the
AppleTalk networking protocol. It includes a daemon to allow Linux
to act as a file server over EtherTalk or IP for Mac's.

%description -l pl
Pakiet ten pozwala na komunikacje kumputerów OS Linux z Macintosh za 
po¶rednictwem protoko³u AppleTalk. Uczyni twojego Linux-a serwerem oraz
klienta plików i wydruków zarówno za po¶rednictwem protoko³u EtherTalk
jaki IP for Mac's.


%package devel
Summary:	Headers and static libraries for Appletalk development
Summary(pl):	Pliki nag³ówkoew i biblioteki statyczne Appletalk
Group:		Development/Libraries
Group(pl):      Programowanie/Biblioteki
Requires:       %{name} = %{version}


%description devel
This packge contains the header files, and static libraries for building
Appletalk networking programs.

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
make OPTOPTS=""

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,pam.d,security,sysconfig,atalk/uams} \
	$RPM_BUILD_ROOT/usr/lib/atalk \
	$RPM_BUILD_ROOT%{_mandir}/{man1,man3,man4,man8}                         


make install INSTALL_PREFIX=$RPM_BUILD_ROOT MANDIR=$RPM_BUILD_ROOT%{_mandir}

(
  cd $RPM_BUILD_ROOT/usr/lib/atalk/filters/
  for i in * ; do
    ln -sf /usr/sbin/psf $i
  done
)

install  config/AppleVolumes.default $RPM_BUILD_ROOT/etc/atalk/AppleVolumes.default
install  config/afpd.conf $RPM_BUILD_ROOT/etc/atalk/afpd.conf
install  config/atalkd.conf $RPM_BUILD_ROOT/etc/atalk/atalkd.conf
install  config/papd.conf $RPM_BUILD_ROOT/etc/atalk/papd.conf
install  config/netatalk.pamd $RPM_BUILD_ROOT/etc/pam.d/netatalk

install %{SOURCE1} $RPM_BUILD_ROOT%{_initdir}/atalk
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/netatalk
install %{SOURCE3} $RPM_BUILD_ROOT/etc/atalk/AppleVolumes.system

install -m644 ${RPM_SOURCE_DIR}/ICDumpSuffixMap .

> $RPM_BUILD_ROOT/etc/security/blacklist.netatalk

gzip -9nf $RPM_BUILD_ROOT/%{_mandir}/man[1348]/* \
    BUGS CHANGES COPYRIGHT ChangeLog ICDu* \
    README* TODO VERSION services.atalk INSTALL/* || :


mv etc/afpd/uam/README README.uam

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
warning: The DDP services appear to be present in /etc/services.
warning: Please check them against services.atalk in the documentation.
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
    rm /tmp/services.tmp$$
  else
    cat <<'_EOD3_' >&2
warning: Unable to find the lines `# start of DDP services' and
warning: `# end of DDP services' in the file /etc/services.
warning: You should remove the DDP services from /etc/service manually.
_EOD3_
  fi
fi


%files
%defattr(644,root,root,755)
%doc {BUGS,CHANGES,COPYRIGHT,ChangeLog,README*,TODO,VERSION,services.atalk,ICDumpSuffixMap}.gz INSTALL 

%dir /etc/atalk
%dir /etc/atalk/uams
%config(noreplace) %verify(not size mtime md5)/etc/atalk/AppleVolumes.default
%config(noreplace) %verify(not size mtime md5)/etc/atalk/AppleVolumes.system
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/netatalk
%config(noreplace) %verify(not size mtime md5) /etc/atalk/afpd.conf
%config(noreplace) %verify(not size mtime md5) /etc/atalk/atalkd.conf
%config(noreplace) %verify(not size mtime md5) /etc/atalk/papd.conf

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
%defattr(-,root,root)
%{_libdir}/libatalk.a
%{_libdir}/libatalk_p.a
%{_includedir}/atalk/
%{_includedir}/netatalk/

%changelog

* %{date} PLD Team <pld-list@pld.org.pl>

$Log: netatalk.spec,v $
Revision 1.1  2000-10-16 20:27:37  kloczek
- spec prepared by marekk@takt.com.pl.

Revision 1.00  2000/08/17 12:58:30  marekk@takt.com.pl
-adaptarised to PLD spec
-remove Rewhide pam and added PLD
-adaprarised netatalk.init


* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- fixed broken PreReq, now PreReq's /etc/init.d

* Tue Jun 27 2000 Than Ngo <than@redhat.de>
- remove prereq initscripts, add requires initscripts
- clean up specfile

* Mon Jun 26 2000 Than Ngo <than@redhat.de>
- /etc/rc.d/init.d -> /etc/init.d
- add condrestart directive
- fix post/preun/postun scripts
- prereq initscripts >= 5.20

* Tue Jun 20 2000 Tim Powers <timp@redhat.com>
- fixed bug 11420 concerning the building with -O2.

* Thu Jun 8 2000 Tim Powers <timp@redhat.com>
- fix bug #11978 
- fix man page locations to be FHS compliant

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- modify PAM setup to use system-auth

* Thu Dec 16 1999 Tim Powers <timp@redhat.com>
- renewed source so it is pristine, delete the problematic files in spec file
	instead
- general spec file cleanups, create buildroot and dirs in the %install
	section
- strip binaries
- gzip man pages
- fixed netatalk-asun.librpcsvc.patch, -lnss_nis too
- changed group
- added %defattr to %files section

* Tue Aug 3 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- rpm-3.0 needs to remove vogus files from source.
  Removed files: etc/papd/.#magics.c, etc/.#diff
* Fri Jul 30 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Change Copyright tag to BSD.
  Add /usr/bin/adv1tov2.
* Thu Apr 22 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Correct librpcsvc.patch.  Move %changelog section last.
  Uncomment again -DNEED_QUOTA_WRAPPER in sys/linux/Makefile since
  LinuxPPC may need.
* Wed Mar 31 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Comment out -DNEED_QUOTA_WRAPPER in sys/linux/Makefile.
* Sat Mar 20 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Correct symbolic links to psf.
  Remove asciize function from nbplkup so as to display Japanese hostname.
* Thu Mar 11 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Included MacPerl 5 script ICDumpSuffixMap which dumps suffix mapping
  containd in Internet Config Preference.
* Tue Mar 2 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- [asun2.1.3]
* Mon Feb 15 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2-8]
* Sun Feb 7 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2-6]
* Mon Jan 25 1999 iNOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2-3]
* Thu Dec 17 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2]
  Remove crlf patch. It is now a server's option.
* Thu Dec 3 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use stable version source netatalk-1.4b2+asun2.1.1.tar.gz
  Add uams directory
* Sat Nov 28 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.1-3 source.
* Mon Nov 23 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.1-2 source.
* Mon Nov 16 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Fix rcX.d's symbolic links.
* Wed Oct 28 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0a-2 source. Remove '%exclusiveos linux' line.
* Sat Oct 24 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use stable version source netatalk-1.4b2+asun2.1.0.tar.gz.
* Mon Oct 5 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-10a source.
* Thu Sep 19 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-8 source. Add chkconfig support.
* Sat Sep 12 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Comment out -DCRLF. Use RPM_OPT_FLAGS.
* Mon Sep 8 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-7 source. Rename atalk.init to atalk.
* Mon Aug 22 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-6 source.
* Mon Jul 27 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-5 source.
* Tue Jul 21 1998 INOUE Koichi <inoue@ma.ns.musashi-techa.c.jp>
- Use pre-asun2.1.0-3 source.
* Tue Jul 7 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Add afpovertcp entries to /etc/services
- Remove BuildRoot in man8 pages
* Mon Jun 29 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use modified sources 1.4b2+asun2.1.0 produced by Adrian Sun
  <asun@saul9.u.washington.edu> to provide an AppleShareIP file server
- Included AppleVolumes.system file maintained by Johnson
  <johnson@stpt.usf.edu>
* Mon Aug 25 1997 David Gibson <D.Gibson@student.anu.edu.au>
- Used a buildroot
- Use RPM_OPT_FLAGS
- Moved configuration parameters/files from atalk.init to /etc/atalk
- Separated devel package
- Built with shared libraries
* Sun Jul 13 1997 Paul H. Hargrove <hargrove@sccm.Stanford.EDU>
- Updated sources from 1.3.3 to 1.4b2
- Included endian patch for Linux/SPARC
- Use all the configuration files supplied in the source.  This has the
  following advantages over the ones in the previous rpm release:
	+ The printer 'lp' isn't automatically placed in papd.conf
	+ The default file conversion is binary rather than text.
- Automatically add and remove DDP services from /etc/services
- Placed the recommended /etc/services in the documentation
- Changed atalk.init to give daemons a soft kill
- Changed atalk.init to make configuration easier

* Wed May 28 1997 Mark Cornick <mcornick@zorak.gsfc.nasa.gov>
Updated for /etc/pam.d
