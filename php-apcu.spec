%define _disable_ld_no_undefined 1

%define realname apcu (APC User Cache)
%define modname apcu
%define inifile 99_%{modname}.ini

Summary:	The %{realname} module for PHP
Name:		php-%{modname}
Epoch:		1
Version:	5.1.21
Release:	2
Group:		Development/PHP
License:	PHP License
Url:		http://pecl.php.net/package/APCu
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
Source1:	apcu.ini
Source2:        %{modname}-panel.conf
Source3:        %{modname}.conf.php
BuildRequires:  php-devel >= 3:5.2.0
Conflicts:	php-afterburner
Conflicts:	php-mmcache
Conflicts:	php-eaccelerator

%description
APC was conceived of to provide a way of boosting the performance of PHP on
heavily loaded sites by providing a way for scripts to be cached in a compiled
state, so that the overhead of parsing and compiling can be almost completely
eliminated. There are commercial products which provide this functionality, but
they are neither open-source nor free. Our goal was to level the playing field
by providing an implementation that allows greater flexibility and is
universally accessible. 

NOTE!: %{name} has to be loaded last, very important!

This package comes with four different flavours of APC (use only one of them):

 o apc-mmap.so - mmap (fcntl) based locks (default)
 o apc-sem.so - IPC semamphore based locks
 o apc-spinlocks.so - Hardware-dependent implementation of spinlocks
 o apc-pthread.so - NPTL pthread mutex based locks
 o apc-mmap+mutex.so - mmap (fcntl) and pthread mutex based locks

%package	panel
Summary:	Web admin GUI for %{realname}
Group:		Development/PHP
Requires:	apache-mod_php
Requires:	%{name} = %{EVRD}

%description	panel
This package contains a Web admin GUI for %{realname}.

To access the web GUI please open up your favourite web browser and point to:

http://localhost/%{name}/

%prep
%setup -qn %{modname}-%{version}

cp %{SOURCE1} %{inifile}

%build
%serverbuild

phpize

%configure \
	--enable-%{modname}=shared,%{_prefix} 
%make

%install
install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}/var/www/%{name}
install -d %{buildroot}/var/lib/php-apc

install -m0644 %{inifile} %{buildroot}%{_sysconfdir}/php.d/%{inifile}

install -m0755 modules/apcu.so %{buildroot}%{_libdir}/php/extensions/apcu.so

# Install the Control Panel
# Pages
install -D -m 644 -p apc.php  \
        %{buildroot}%{_datadir}/apcu-panel/index.php
# Apache config
install -D -m 644 -p %{SOURCE2} \
        %{buildroot}%{_sysconfdir}/httpd/conf.d/apcu-panel.conf
# Panel config
install -D -m 644 -p %{SOURCE3} \
        %{buildroot}%{_sysconfdir}/apcu-panel/conf.php

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%files
%doc tests README.md LICENSE NOTICE TECHNOTES.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/apcu.so
%attr(0755,apache,apache) /var/lib/php-apc

%files panel
# Need to restrict access, as it contains a clear password
%attr(550,apache,root) %dir %{_sysconfdir}/apcu-panel
%config(noreplace) %{_sysconfdir}/apcu-panel/conf.php
%config(noreplace) %{_sysconfdir}/httpd/conf.d/apcu-panel.conf
%{_datadir}/apcu-panel

