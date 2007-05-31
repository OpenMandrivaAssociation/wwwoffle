%define	version	2.9b
%define	release	%mkrel 1
%define	name	wwwoffle

Summary:	WWW Offline Explorer - Caching Web Proxy Server
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		Networking/Other
Source0:	ftp://ftp.ibiblio.org/pub/Linux/apps/www/servers/%name-%version.tar.bz2
Source1:	%{name}-initfile
URL:		http://www.gedanken.demon.co.uk/wwwoffle/
Buildrequires:	flex
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires:	htdig
 
%description
A proxy HTTP/FTP server for computers with dial-up internet access.
- Caching of pages viewed while connected for review later.
- Browsing of cached pages while not connected, with the ability
  to follow links and mark other pages for download.
- Downloading of specified pages non-interactively.
- Multiple indices of pages stored in cache for easy selection.
- Interactive or command line option to select pages for fetching
  individually or recursively.
- All options controlled using a simple configuration file with a
  web page to edit it.

%prep
%setup -q

%build
%configure

%make all \
	CFLAGS="$RPM_OPT_FLAGS"
	INSTDIR=/usr \
	SPOOLDIR=/var/spool/wwwoffle \
	CONFDIR=%{_sysconfdir} \
	MANDIR=%{_mandir}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/var/spool/
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/cron.{daily,weekly}
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man[158]

%{makeinstall_std} \
	INSTDIR=$RPM_BUILD_ROOT%{_prefix} \
	SPOOLDIR=$RPM_BUILD_ROOT/var/spool/wwwoffle \
	CONFDIR=$RPM_BUILD_ROOT%{_sysconfdir} \
	MANDIR=$RPM_BUILD_ROOT%{_mandir}


#install -m 755 upgrade* $RPM_BUILD_ROOT/usr/sbin/

cp %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/wwwoffled

cat > $RPM_BUILD_ROOT%{_sysconfdir}/cron.weekly/%{name} <<EOF
#!/bin/sh
%{_bindir}/wwwoffle -purge
EOF

cat > $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/%{name} <<EOF
#!/bin/sh
/var/spool/wwwoffle/html/search/htdig/scripts/wwwoffle-htdig-full
EOF

perl -pi -e 's|'$RPM_BUILD_ROOT'||g' \
	$RPM_BUILD_ROOT%{_sysconfdir}/wwwoffle.conf \
	$RPM_BUILD_ROOT%{_mandir}/man5/wwwoffle.conf.5 \
	$RPM_BUILD_ROOT/var/spool/wwwoffle/html/search/htdig/conf/*.conf \
	$RPM_BUILD_ROOT/var/spool/wwwoffle/html/search/htdig/scripts/*

# remove unwanted filde
rm -rf $RPM_BUILD_ROOT/usr/doc
rm -rf $RPM_BUILD_ROOT/var/spool/wwwoffle/outgoing/*


%post
/sbin/chkconfig --add wwwoffled
if [ $1 = 0 ]; then
	%{_initrddir}/wwwoffled start
fi

%preun
%{_initrddir}/wwwoffled status | grep running && %{_initrddir}/wwwoffled stop
if [ $1 = 0 ]; then    
	# execute this only if we are NOT doing an upgrade
	/sbin/chkconfig --del wwwoffled
fi          

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%dir /var/spool/wwwoffle
%dir /var/spool/wwwoffle/html
%doc /var/spool/wwwoffle/html/*
%dir /var/spool/wwwoffle/http
%dir /var/spool/wwwoffle/lasttime
%dir /var/spool/wwwoffle/monitor
%dir /var/spool/wwwoffle/outgoing
/var/spool/wwwoffle/search
%doc doc/README* doc/FAQ doc/INSTALL doc/NEWS ChangeLog doc/CHANGES.CONF
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/wwwoffle.conf
%attr(755,root,root) %config(noreplace) %{_initrddir}/wwwoffled
%attr(755,root,root) %config(missingok,noreplace) %{_sysconfdir}/cron.daily/%{name}
%attr(755,root,root) %config(missingok,noreplace) %{_sysconfdir}/cron.weekly/%{name}
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*


