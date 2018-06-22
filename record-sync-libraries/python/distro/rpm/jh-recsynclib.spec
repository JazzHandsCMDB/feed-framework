%global _git_repo jh-recsynclib
%global filelist %{pkgname}-%{version}-filelist

Name:           python2.7-jh-recsynclib
Version:        0.1.0
Release:        1
Summary:        JazzHands Record Synchronization Library

Group:          Applications
License:        ASL 2.0
Url:            https://github.com/JazzHandsCMDB/feed-framework
Source0:        %{_git_repo}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:      noarch
BuildRequires:  python2.7
Requires:       python2.7, python2.7-future

%description
JazzHands Python based synchronization library. Gluing things together since 2017

%prep
%setup -q -n %{_git_repo}-%{version}

%install
python2.7 ./setup.py install --root=%{buildroot} --optimize=1 --record=%{filelist}

%files -f %{filelist}

%changelog
* Fri Oct 13 2017 Ryan D Williams <rdw@drws-office.com> 0.1.0
  - Initial Release