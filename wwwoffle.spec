Summary:	WWW Offline Explorer - Caching Web Proxy Server
Name:		wwwoffle
Version:	2.9i
Release:	3
License:	GPLv2
Group:		Networking/Other
Source0:	ftp://ftp.ibiblio.org/pub/Linux/apps/www/servers/%{name}-%{version}.tgz
Source1:	%{name}.service
URL:		http://www.gedanken.demon.co.uk/%{name}/
Buildrequires:	flex
Buildrequires:	htdig-devel
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
%configure2_5x

%make all \
	CFLAGS="%{optflags}"
	INSTDIR=/usr \
	SPOOLDIR=/var/spool/wwwoffle \
	CONFDIR=%{_sysconfdir} \
	MANDIR=%{_mandir}

%install
mkdir -p %{buildroot}/var/spool/
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/cron.{daily,weekly}
mkdir -p %{buildroot}%{_mandir}/man[158]

%makeinstall_std \
	INSTDIR=%{buildroot}%{_prefix} \
	SPOOLDIR=%{buildroot}/var/spool/wwwoffle \
	CONFDIR=%{buildroot}%{_sysconfdir} \
	MANDIR=%{buildroot}%{_mandir}


#install -m 755 upgrade* $RPM_BUILD_ROOT/usr/sbin/

mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE1} %{buildroot}%{_unitdir}/wwwoffled.service

cat > %{buildroot}%{_sysconfdir}/cron.weekly/%{name} <<EOF
#!/bin/sh
%{_bindir}/wwwoffle -purge
EOF

cat > %{buildroot}%{_sysconfdir}/cron.daily/%{name} <<EOF
#!/bin/sh
/var/spool/wwwoffle/html/search/htdig/scripts/wwwoffle-htdig-full
EOF

perl -pi -e 's|'%{buildroot}'||g' \
	%{buildroot}%{_sysconfdir}/wwwoffle.conf \
	%{buildroot}%{_mandir}/man5/wwwoffle.conf.5 \
	%{buildroot}/var/spool/wwwoffle/html/search/htdig/conf/*.conf \
	%{buildroot}/var/spool/wwwoffle/html/search/htdig/scripts/*

# remove unwanted filde
rm -rf %{buildroot}/usr/doc
rm -rf %{buildroot}/var/spool/wwwoffle/outgoing/*

%post
%systemd_post %{name}d.service

%preun
%systemd_preun %{name}d.service

%postun
%systemd_postun_with_restart %{name}d.service

%files
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
%{_unitdir}/wwwoffled*
%attr(755,root,root) %config(missingok,noreplace) %{_sysconfdir}/cron.daily/%{name}
%attr(755,root,root) %config(missingok,noreplace) %{_sysconfdir}/cron.weekly/%{name}
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
