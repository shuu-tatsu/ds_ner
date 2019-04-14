from flair.embeddings import TokenEmbeddings
from flair.data import Dictionary
from flair.models import SequenceTagger
from flair.models.sequence_tagger_model import START_TAG, STOP_TAG
import numpy as np
import torch
import flair

UNK_TAG: str = '<unk>'

class UnkTagger(SequenceTagger):

    def __init__(self,
                 hidden_size: int,
                 embeddings: TokenEmbeddings,
                 tag_dictionary: Dictionary,
                 tag_type: str,
                 use_crf: bool = True,
                 use_rnn: bool = True,
                 rnn_layers: int = 1,
                 dropout: float = 0.0,
                 word_dropout: float = 0.05,
                 locked_dropout: float = 0.5,
                 pickle_module: str = 'pickle'
                 ):

        super(UnkTagger, self).__init__(
                 hidden_size,
                 embeddings,
                 tag_dictionary,
                 tag_type,
                 use_crf,
                 use_rnn,
                 rnn_layers,
                 dropout,
                 word_dropout,
                 locked_dropout,
                 pickle_module
                 )

        #self.e = (0.1)**40
        self.e = 1. / np.finfo(np.float32).max
        self.unk_tag = self.tag_dictionary.get_idx_for_item(UNK_TAG)
        mask = self.get_trans_mask()
        self.valid_trans = torch.tensor(mask,
                                        dtype=self.transitions.dtype,
                                        device=flair.device)

    def get_trans_mask(self):
        mask = np.zeros((self.tagset_size,)*4)
        for bf in range(self.tagset_size):
            mask[self.unk_tag,bf,:,bf] = 1
            for c in range(self.tagset_size):
                mask[c,bf,c,bf] = 1
        for c in range(self.tagset_size):
            mask[c,self.unk_tag,c,:] = 1
        return mask

    def _score_sentence(self, feats, tags, lens_):

        init_alphas = torch.FloatTensor(self.tagset_size).fill_(-10000.)
        init_alphas[self.tag_dictionary.get_idx_for_item(START_TAG)] = 0.

        forward_var = torch.zeros(
            feats.shape[0],
            feats.shape[1] + 1,
            feats.shape[2],
            dtype=torch.float, device=flair.device)

        forward_var[:, 0, :] = init_alphas[None, :].repeat(feats.shape[0], 1)

        transitions = self.transitions.view(
            1,
            self.transitions.shape[0],
            self.transitions.shape[1],
        ).repeat(feats.shape[0], 1, 1)

        '''
        #for debug
        tags[0,1] = self.unk_tag
        tags[0,lens_[0]-1] = self.unk_tag
        ##################
        '''

        start_tag = torch.full(
            (feats.shape[0], 1),
            self.tag_dictionary.get_idx_for_item(START_TAG),
            dtype=tags.dtype,
            device=flair.device)
        forward_tags = torch.cat([start_tag, tags], dim=1)
        masks = torch.stack([torch.stack([
              self.valid_trans[it[i+1],it[i]]\
              for i in range(feats.shape[1])], dim=0)
              for it in torch.unbind(forward_tags, dim=0)], dim=0)

        '''
        #for debug
        for i in range(3):
            print('\n{}th tags[0] {}:{} -> {}:{}'.format(
                     i,
                     forward_tags[0,i], self.tag_dictionary.get_item_for_index(forward_tags[0,i]),
                     forward_tags[0,i+1], self.tag_dictionary.get_item_for_index(forward_tags[0,i+1])))
            for c,bf in zip(*np.where(masks[0,i].cpu().numpy())):
                print('    {}:{} -> {}:{}'.format(
                         bf, self.tag_dictionary.get_item_for_index(bf),
                         c, self.tag_dictionary.get_item_for_index(c)))
        ##################
        '''

        for i in range(feats.shape[1]):
            emit_score = feats[:, i, :]

            tag_var = \
                emit_score[:, :, None].repeat(1, 1, transitions.shape[2]) + \
                transitions + \
                forward_var[:, i, :][:, :, None].repeat(1, 1, transitions.shape[2]).transpose(2, 1)

            max_tag_var, _ = torch.max(tag_var, dim=2)

            tag_var = tag_var - \
                      max_tag_var[:, :, None].repeat(1, 1, transitions.shape[2])

            '''
            #for debug
            if i < 3:
                print('\n{}th torch.exp(tag_var[0])*masks[0] {}:{} -> {}:{}'.format(
                         i,
                         forward_tags[0,i], self.tag_dictionary.get_item_for_index(forward_tags[0,i]),
                         forward_tags[0,i+1], self.tag_dictionary.get_item_for_index(forward_tags[0,i+1])))
                for c,bf in zip(*np.where((torch.exp(tag_var[0])*masks[0,i]).cpu().detach().numpy())):
                    print('    {}:{} -> {}:{}'.format(
                             bf, self.tag_dictionary.get_item_for_index(bf),
                             c, self.tag_dictionary.get_item_for_index(c)))
            ##################
            '''

            result = (torch.sum(torch.exp(tag_var)*masks[:,i], dim=2)) + self.e

            '''
            for i in range(result.shape[0]):
                if (result[i] == 0).max():
                    print(i)
                    print(masks[i])

            assert not (result == 0).max()
            '''

            agg_ = torch.log(torch.sum(torch.exp(tag_var)*masks[:,i], dim=2) + self.e)

            cloned = forward_var.clone()
            cloned[:, i + 1, :] = max_tag_var + agg_

            forward_var = cloned

        forward_var = forward_var[range(forward_var.shape[0]), lens_, :]

        terminal_var = forward_var + \
                       self.transitions[self.tag_dictionary.get_idx_for_item(STOP_TAG)][None, :].repeat(
                           forward_var.shape[0], 1)
        '''
        #for debug
        print('alpha[0] = {} if the last tag is <unk> else {}'.format(
                 torch.log(torch.sum(torch.exp(terminal_var[0]))).detach(),
                 terminal_var[0,forward_tags[0,lens_[0]]].detach()
        ))
        ##################
        '''

        '''
        for i in range(terminal_var.shape[0]):
            result = torch.sum(torch.exp(terminal_var[i])) + self.e
            assert not (result == 0).max()
        '''

        alpha = torch.stack([
              torch.log(torch.sum(torch.exp(terminal_var[i])) + self.e)\
              if forward_tags[i, lens_[i]] == self.unk_tag\
              else terminal_var[i,forward_tags[i, lens_[i]]]
              for i in range(terminal_var.shape[0])], dim=0)

        '''
        #for debug
        print('tags[0,lens_[0]-1] {}:{}, alpha[0] {}'.format(
                 tags[0,lens_[0]-1],
                 self.tag_dictionary.get_item_for_index(tags[0,lens_[0]-1]),
                 alpha[0].detach()))
        #exit()
        ##################
        '''
        return alpha
