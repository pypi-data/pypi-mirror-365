# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Sensitive filesystem locations relative to user homes. '''


from . import __


_scribe = __.produce_scribe( __name__ )


def discover_sensitive_locations( ) -> frozenset[ str ]:
    ''' Discovers sensitive locations relative to user home. '''
    return frozenset( (
        # Credentials and Keys
        '.ssh', '.aws', '.gnupg', '.gpg',
        # Cloud Services
        '.config/gcloud', '.azure', '.kube',
        '.terraform.d', '.chef',
        # Package Managers
        '.npm', '.pip', '.cargo', '.gem',
        '.gradle', '.m2', '.ivy2',
        # Browser Data
        '.mozilla', '.chrome', '.config/chromium',
        '.netscape', '.opera',
        # Database
        '.postgresql', '.mysql', '.redis',
        # Shell History and Config
        '.bash_history', '.zsh_history',
        '.bashrc', '.zshrc', '.profile',
        # Cryptocurrency
        '.bitcoin', '.ethereum',
        # Other Sensitive
        '.password-store', '.secrets', '.keys',
        '.config', '.local/share',
    ) )
