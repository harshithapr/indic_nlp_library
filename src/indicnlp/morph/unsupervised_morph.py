# Copyright Anoop Kunchukuttan 2014 - present
#
# This file is part of Indic NLP Library.
# 
# Indic NLP Library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Indic NLP Library is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
# 
#        You should have received a copy of the GNU General Public License
#        along with Indic NLP Library.  If not, see <http://www.gnu.org/licenses/>.
#

import codecs, sys, itertools,string,re
import morfessor 
from indicnlp import langinfo
from indicnlp import common
from indicnlp.tokenize import indic_tokenize

# Unsupervised Morphological Analyser for Indian languages. 
#
# @author Anoop Kunchukuttan 
#

class MorphAnalyzerI(object):
    """
     Interface for Morph Analyzer
    """

    def morph_analyze(word):
        pass 

    def morph_analyze_document(tokens):
        pass 

class UnsupervisedMorphAnalyzer(MorphAnalyzerI): 
    """
    Unsupervised Morphological analyser built using Morfessor 2.0
    """

    def __init__(self,lang,add_marker=False): 
        self.lang=lang
        self.add_marker=add_marker

        io = morfessor.MorfessorIO()
        self._morfessor_model=io.read_any_model(common.INDIC_RESOURCES_PATH+'/morph/morfessor/{}.model'.format(lang))

        self._script_range_pat=ur'^[{}-{}]+$'.format(unichr(langinfo.SCRIPT_RANGES[lang][0]),unichr(langinfo.SCRIPT_RANGES[lang][1]))
        self._script_check_re=re.compile(self._script_range_pat)

    def _contains_number(self,text):
        if self.lang in langinfo.SCRIPT_RANGES: 
            for c in text: 
                offset=ord(c)-langinfo.SCRIPT_RANGES[self.lang][0]
                if offset >=langinfo.NUMERIC_OFFSET_START and offset <= langinfo.NUMERIC_OFFSET_END:
                    return True  
        return False     

    def _morphanalysis_needed(self,word):
        return self._script_check_re.match(word) and not self._contains_number(word)

    def morph_analyze(self,word):
        """
        Morphanalyzes a single word and returns a list of component morphemes

        @param word: string input word 
        """
        m_list=[]
        if self._morphanalysis_needed(word): 
            val=self._morfessor_model.viterbi_segment(word)
            m_list=val[0]
            if self.add_marker:
                m_list= [ u'{}_S_'.format(m) if i>0 else u'{}_R_'.format(m)  for i,m in enumerate(m_list)]
        else:
            if self.add_marker:
                word=u'{}_E_'.format(word)
            m_list=[word]
        return m_list 

        ### Older implementation
        #val=self._morfessor_model.viterbi_segment(word)
        #m_list=val[0]
        #if self.add_marker:
        #    m_list= [ u'{}_S_'.format(m) if i>0 else u'{}_R_'.format(m)  for i,m in enumerate(m_list)]
        #return m_list
    

    def morph_analyze_document(self,tokens):
        """
        Morphanalyzes a document, represented as a list of tokens
        Each word  is morphanalyzed and result is a list of morphemes constituting the document 

        @param tokens: string sequence of words 

        @return list of segmentations for each word. Each segmentation is a list of the morphs of the word. 
        """

        out_tokens=[]
        for token in tokens: 
            morphs=self.morph_analyze(token)
            out_tokens.append(morphs)
        return out_tokens    

        #### Older implementation
        #out_tokens=[]
        #for token in tokens: 
        #    if self._morphanalysis_needed(token): 
        #        morphs=self.morph_analyze(token)
        #        out_tokens.extend(morphs)
        #    else:
        #        if self.add_marker:
        #            token=u'{}_E_'.format(token)
        #        out_tokens.append(token)
        #return out_tokens    


if __name__ == '__main__': 

    if len(sys.argv)<4:
        print "Usage: python unsupervised_morph.py <infile> <outfile> <language> <indic_resources_path> [<add_marker>]"
        sys.exit(1)

    language=sys.argv[3]
    common.INDIC_RESOURCES_PATH=sys.argv[4]

    add_marker=False

    if len(sys.argv)==6:
        add_marker= True if sys.argv[5] == 'True' else False 

    analyzer=UnsupervisedMorphAnalyzer(language,add_marker)

    with codecs.open(sys.argv[1],'r','utf-8') as ifile:
        with codecs.open(sys.argv[2],'w','utf-8') as ofile:
            for line in ifile.readlines():
                line=line.strip()
                tokens=indic_tokenize.trivial_tokenize(line)
                morph_tokens=analyzer.morph_analyze_document(tokens)
                ofile.write(string.join(morph_tokens,sep=' '))
                ofile.write('\n')

