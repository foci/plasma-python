from plasma.primitives.shots import ShotListFiles
from data.signals import *

import getpass
import uuid
import yaml

import hashlib

def parameters(input_file):
    """Parse yaml file of configuration parameters."""
    from plasma.models.targets import HingeTarget, MaxHingeTarget, BinaryTarget, TTDTarget, TTDInvTarget, TTDLinearTarget

    with open(input_file, 'r') as yaml_file:
        params = yaml.load(yaml_file)

        params['user_name'] = getpass.getuser()
        output_path = params['fs_path'] #+ "/" + params['user_name']
        base_path = output_path

        params['paths']['base_path'] = base_path
        params['paths']['signal_prepath'] = base_path + params['paths']['signal_prepath']
        params['paths']['shot_list_dir'] = base_path + params['paths']['shot_list_dir']
        params['paths']['output_path'] = output_path
        h = get_unique_signal_hash(all_signals.values())
        params['paths']['global_normalizer_path'] = output_path + '/normalization/normalization_signal_group_{}.npz'.format(h)
        if params['training']['hyperparam_tuning']:
            # params['paths']['saved_shotlist_path'] = './normalization/shot_lists.npz'
            params['paths']['normalizer_path'] = './normalization/normalization_signal_group_{}.npz'.format(h)
            params['paths']['model_save_path'] = './model_checkpoints/'
            params['paths']['csvlog_save_path'] = './csv_logs/'
            params['paths']['results_prepath'] = './results/'
        else:
            # params['paths']['saved_shotlist_path'] = output_path +'/normalization/shot_lists.npz'
            params['paths']['normalizer_path'] = params['paths']['global_normalizer_path']
            params['paths']['model_save_path'] = output_path + '/model_checkpoints/'
            params['paths']['csvlog_save_path'] = output_path + '/csv_logs/'
            params['paths']['results_prepath'] = output_path + '/results/'
        params['paths']['tensorboard_save_path'] = output_path + params['paths']['tensorboard_save_path']
        params['paths']['saved_shotlist_path'] = params['paths']['base_path'] + '/processed_shotlists/' + params['paths']['data'] + '/shot_lists_signal_group_{}.npz'.format(h)
        params['paths']['processed_prepath'] = output_path +'/processed_shots/' + 'signal_group_{}/'.format(h)

        #ensure shallow model has +1 -1 target.
        if params['model']['shallow'] or params['target'] == 'hinge':
            params['data']['target'] = HingeTarget
        elif params['target'] == 'maxhinge':
            MaxHingeTarget.fac = params['data']['positive_example_penalty']
            params['data']['target'] = MaxHingeTarget
        elif params['target'] == 'binary':
            params['data']['target'] = BinaryTarget
        elif params['target'] == 'ttd':
            params['data']['target'] = TTDTarget
        elif params['target'] == 'ttdinv':
            params['data']['target'] = TTDInvTarget
        elif params['target'] == 'ttdlinear':
            params['data']['target'] = TTDLinearTarget
        else:
            print('Unkown type of target. Exiting')
            exit(1)

        #params['model']['output_activation'] = params['data']['target'].activation
        #binary crossentropy performs slightly better?
        #params['model']['loss'] = params['data']['target'].loss

        #signals
        params['paths']['all_signals_dict'] = all_signals
        #assert order q95,li,ip,lm,betan,energy,dens,pradcore,pradedge,pin,pechin,torquein,ipdirect,etemp_profile,edens_profile

        #shot lists
        jet_carbon_wall = ShotListFiles(jet,params['paths']['shot_list_dir'],['CWall_clear.txt','CFC_unint.txt'],'jet carbon wall data')
        jet_iterlike_wall = ShotListFiles(jet,params['paths']['shot_list_dir'],['ILW_unint.txt','BeWall_clear.txt'],'jet iter like wall data')

        jenkins_jet_carbon_wall = ShotListFiles(jet,params['paths']['shot_list_dir'],['jenkins_CWall_clear.txt','jenkins_CFC_unint.txt'],'Subset of jet carbon wall data for Jenkins tests')
        jenkins_jet_iterlike_wall = ShotListFiles(jet,params['paths']['shot_list_dir'],['jenkins_ILW_unint.txt','jenkins_BeWall_clear.txt'],'Subset of jet iter like wall data for Jenkins tests')

        jet_full = ShotListFiles(jet,params['paths']['shot_list_dir'],['ILW_unint.txt','BeWall_clear.txt','CWall_clear.txt','CFC_unint.txt'],'jet full data')

        d3d_10000 = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_10000.txt','d3d_disrupt_10000.txt'],'d3d data 10000 ND and D shots')
        d3d_1000 = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_1000.txt','d3d_disrupt_1000.txt'],'d3d data 1000 ND and D shots')
        d3d_100 = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_100.txt','d3d_disrupt_100.txt'],'d3d data 100 ND and D shots')
        d3d_full = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_data_avail.txt','d3d_disrupt_data_avail.txt'],'d3d data since shot 125500')
        d3d_jenkins = ShotListFiles(d3d,params['paths']['shot_list_dir'],['jenkins_d3d_clear.txt','jenkins_d3d_disrupt.txt'],'Subset of d3d data for Jenkins test')
        d3d_cem = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_data_avail_cem2.txt','d3d_disrupt_data_avail_cem2.txt'],'d3d data since shot 125500')
        d3d_kag = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_data_avail_kag.txt','d3d_disrupt_data_avail_kag.txt'],'d3d data since shot 125500')
        d3d_kag_d = ShotListFiles(d3d,params['paths']['shot_list_dir'],['d3d_clear_kag.txt','d3d_disrupt_kag.txt'],'d3d test data')

        d3d_jb_full = ShotListFiles(d3d,params['paths']['shot_list_dir'],['shotlist_JaysonBarr_clear.txt','shotlist_JaysonBarr_disrupt.txt'],'d3d shots since 160000-170000')

        nstx_full = ShotListFiles(nstx,params['paths']['shot_list_dir'],['disrupt_nstx.txt'],'nstx shots (all are disruptive')
 
        if params['paths']['data'] == 'jet_data':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = jet_signals
        elif params['paths']['data'] == 'jet_data_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = jet_signals_0D
        elif params['paths']['data'] == 'jet_data_1D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = jet_signals_1D
        elif params['paths']['data'] == 'jet_carbon_data':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = jet_signals
        elif params['paths']['data'] == 'jet_mixed_data':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = jet_signals
        elif params['paths']['data'] == 'jenkins_jet':
            params['paths']['shot_files'] = [jenkins_jet_carbon_wall]
            params['paths']['shot_files_test'] = [jenkins_jet_iterlike_wall]
            params['paths']['use_signals_dict'] = jet_signals
        elif params['paths']['data'] == 'jet_data_fully_defined': #jet data but with fully defined signals
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = fully_defined_signals
        elif params['paths']['data'] == 'jet_data_fully_defined_0D': #jet data but with fully defined signals
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = fully_defined_signals_0D



        elif params['paths']['data'] == 'd3d_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = {'q95':q95,'li':li,'ip':ip,'lm':lm,'betan':betan,'energy':energy,'dens':dens,'pradcore':pradcore,'pradedge':pradedge,'pin':pin,'torquein':torquein,'ipdirect':ipdirect,'iptarget':iptarget,'iperr':iperr,
'etemp_profile':etemp_profile ,'edens_profile':edens_profile}
        elif params['paths']['data'] == 'd3d_data_1D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = {'ipdirect':ipdirect,'etemp_profile':etemp_profile ,'edens_profile':edens_profile}
        elif params['paths']['data'] == 'd3d_data_all_profiles':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = {'ipdirect':ipdirect,'etemp_profile':etemp_profile ,'edens_profile':edens_profile,'itemp_profile':itemp_profile,'zdens_profile':zdens_profile,'trot_profile':trot_profile,'pthm_profile':pthm_profile,'neut_profile':neut_profile,'q_profile':q_profile,'bootstrap_current_profile':bootstrap_current_profile,'q_psi_profile':q_psi_profile}
        elif params['paths']['data'] == 'd3d_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = {'q95':q95,'li':li,'ip':ip,'lm':lm,'betan':betan,'energy':energy,'dens':dens,'pradcore':pradcore,'pradedge':pradedge,'pin':pin,'torquein':torquein,'ipdirect':ipdirect,'iptarget':iptarget,'iperr':iperr}
        elif params['paths']['data'] == 'd3d_data_all':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = d3d_signals
        elif params['paths']['data'] == 'jenkins_d3d':
            params['paths']['shot_files'] = [d3d_jenkins]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {'q95':q95,'li':li,'ip':ip,'lm':lm,'betan':betan,'energy':energy,'dens':dens,'pradcore':pradcore,'pradedge':pradedge,'pin':pin,'torquein':torquein,'ipdirect':ipdirect,'iptarget':iptarget,'iperr':iperr,
'etemp_profile':etemp_profile ,'edens_profile':edens_profile}
        elif params['paths']['data'] == 'd3d_data_fully_defined': #jet data but with fully defined signals
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = fully_defined_signals
        elif params['paths']['data'] == 'd3d_data_fully_defined_0D': #jet data but with fully defined signals
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_data_cem':
            params['paths']['shot_files'] = [d3d_cem]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = d3d_signals
        elif params['paths']['data'] == 'd3d_data_kag':
            params['paths']['shot_files'] = [d3d_kag]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = d3d_signals
        elif params['paths']['data'] == 'd3d_data_kag_d':
            params['paths']['shot_files'] = [d3d_kag_d]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = d3d_signals
        #cross-machine
        elif params['paths']['data'] == 'jet_to_d3d_data':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = fully_defined_signals
        elif params['paths']['data'] == 'd3d_to_jet_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = fully_defined_signals
        elif params['paths']['data'] == 'jet_to_d3d_data_0D':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_to_jet_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = fully_defined_signals_0D
        elif params['paths']['data'] == 'jet_to_d3d_data_1D':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = fully_defined_signals_1D
        elif params['paths']['data'] == 'd3d_to_jet_data_1D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = fully_defined_signals_1D



        else: 
            print("Unkown data set {}".format(params['paths']['data']))
            exit(1)

        if len(params['paths']['specific_signals']):
            for sig in params['paths']['specific_signals']:
                if sig not in params['paths']['use_signals_dict'].keys():
                    print("Signal {} is not fully defined for {} machine. Skipping...".format(sig,params['paths']['data'].split("_")[0]))
            params['paths']['specific_signals'] = list(filter(lambda x: x in params['paths']['use_signals_dict'].keys(), params['paths']['specific_signals']))
            selected_signals = {k: params['paths']['use_signals_dict'][k] for k in params['paths']['specific_signals']}
            params['paths']['use_signals'] = sort_by_channels(list(selected_signals.values()))

        else:
            #default case
            params['paths']['use_signals'] = sort_by_channels(list(params['paths']['use_signals_dict'].values()))

        params['paths']['all_signals'] = sort_by_channels(list(params['paths']['all_signals_dict'].values()))

        print("Selected signals (determines which signals training is run on):\n{}".format(params['paths']['use_signals']))

        params['paths']['shot_files_all'] = params['paths']['shot_files']+params['paths']['shot_files_test']
        params['paths']['all_machines'] = list(set([file.machine for file in params['paths']['shot_files_all']]))

        #type assertations
        assert type(params['data']['signal_to_augment']) == str or type(params['data']['signal_to_augment']) == None
        assert type(params['data']['augment_during_training']) == bool

    return params

def get_unique_signal_hash(signals):
    return int(hashlib.md5(''.join(tuple(map(lambda x: x.description, sorted(signals)))).encode('utf-8')).hexdigest(),16)

#make sure 1D signals come last! This is necessary for model builder.
def sort_by_channels(list_of_signals):
    return sorted(list_of_signals,key = lambda x: x.num_channels)

