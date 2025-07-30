import importlib
import os
import re
import sys

from pathlib import Path


def _exit(msg):
    print(msg)
    sys.exit(1)


plugin_name = sys.modules[__name__].__package__.split('.')[0]

target_package = "netbox"
djs = f"{target_package}.settings"
re_plugins = re.compile(r'(?P<prolog>^.*?)\[\s*?(?P<plugins>[^]]*?)](?P<epilog>.*$)', re.MULTILINE)


def post_install():
    home = Path(sys.modules[djs].__file__).parent.parent
    xc = os.system(f'cd {home} && python manage.py migrate {plugin_name} && python manage.py collectstatic --noinput')
    return xc == 0


def install_for_netbox():
    """ Modify the target package configuration after installation """
    # 1. check if netbox is installed
    try:
        from django.core.exceptions import ImproperlyConfigured
    except ImportError:
        return _exit('No netbox package installed (in the current environment)')

    try:
        djs = f"{target_package}.settings"
        nb_settings = importlib.import_module(djs)
        os.environ["DJANGO_SETTINGS_MODULE"] = djs
    except ImportError:
        return _exit('No netbox package installed (in the current environment)')
    except ImproperlyConfigured:
        return _exit('Current netbox configuration is invalid (or cannot be loaded)')

    package_path = Path(nb_settings.__file__).parent
    # Locate configuration file
    config_file = package_path / "configuration.py"
    if not config_file.exists():
        return _exit('This netbox installation has not been configured (yet).')

    try:
        nextbox = importlib.import_module(f"{target_package}.configuration")
    except ImportError:
        return _exit('This netbox installation has no valid configuration.')

    plugins = getattr(nextbox, 'PLUGINS', None)
    if plugins and plugin_name in plugins:
        return _exit(f'Plugin `{plugin_name}` is already installed.')

    go = input('Do you want to install this netbox plugin? [y/N]: ')
    if go != 'y':
        return _exit(f'Plugin `{plugin_name}` plugin not installed')

    config_py = original_config = config_file.read_text()
    if plugins is None:
        config_py += f"\nPLUGINS = [{repr(plugin_name)}]\n"
    else:
        parts = re.split(r'(?P<assigning>PLUGINS\s*=\s*)', config_py, re.MULTILINE)
        assert len(parts) > 1
        last_plugins = parts[-1]
        if m := re.search(re_plugins, last_plugins):
            prolog = m.groupdict()['prolog']
            epilog = m.groupdict()['epilog']
            plugins_array = m.groupdict()['plugins']
            glue = ', ' if plugins_array else ''
            plugins_array += f'{glue}"netpicker"'
            parts[-1] = f"{prolog}[{plugins_array}]{epilog}"
        config_py = "".join(parts)
    config_file.write_text(config_py)
    try:
        importlib.reload(nextbox)
    except ImportError:
        config_file.write_text(original_config)
        _exit('Failed to install netbox plugin')

    if post_install():
        print(f'Plugin `{plugin_name}` installed successfully.')


if __name__ == "__main__":
    install_for_netbox()
